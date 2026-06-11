#!/usr/bin/env python3
"""
Proactive presence snapshot + evaluator + log.

This is the small decision layer for Shelly's Telegram-first proactive behavior:
- build a structured snapshot of Kelly's current state
- evaluate candidate proactive messages
- log what happened so behavior can be reviewed later
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    from message_quality_gate import validate_proactive_message
except ModuleNotFoundError:  # pragma: no cover - import path differs in module tests
    from scripts.message_quality_gate import validate_proactive_message

PROACTIVE_STATE_FILE = "/data/workspace/memory/proactive_state.json"
PROACTIVE_LOG_FILE = "/data/workspace/memory/proactive_message_log.jsonl"


def _ensure_parent(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def parse_compact_kelly_state(kelly_state_text: str) -> Dict[str, str]:
    snapshot = {
        'physical': '',
        'schedule': '',
        'focus': '',
        'tone': '',
        'open_loops': '',
        'avoid': '',
    }

    for line in (kelly_state_text or '').splitlines():
        if ': ' not in line:
            continue
        key, value = line.split(': ', 1)
        normalized = key.strip().lower().replace(' ', '_')
        if normalized in snapshot:
            snapshot[normalized] = value.strip()
    return snapshot


def load_recent_proactive_log(hours: int = 72) -> List[Dict[str, object]]:
    if not os.path.exists(PROACTIVE_LOG_FILE):
        return []

    cutoff = datetime.now() - timedelta(hours=hours)
    items: List[Dict[str, object]] = []
    with open(PROACTIVE_LOG_FILE, 'r') as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = item.get('timestamp')
            if not ts:
                continue
            try:
                when = datetime.fromisoformat(ts)
            except ValueError:
                continue
            if when >= cutoff:
                items.append(item)
    return items


def last_meaningful_send_hours(recent_log: List[Dict[str, object]]) -> Optional[float]:
    sent = [item for item in recent_log if item.get('decision') == 'send']
    if not sent:
        return None
    newest = sent[-1]
    try:
        when = datetime.fromisoformat(str(newest['timestamp']))
    except Exception:
        return None
    return round((datetime.now() - when).total_seconds() / 3600, 2)


def build_snapshot(
    *,
    external_events: Dict[str, object],
    significance_result: Dict[str, object],
    conversation_check: Dict[str, object],
    kelly_state_text: str,
    recent_activity: Dict[str, object],
    candidates: List[Dict[str, str]],
) -> Dict[str, object]:
    recent_log = load_recent_proactive_log()
    parsed_state = parse_compact_kelly_state(kelly_state_text)
    snapshot: Dict[str, object] = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'telegram_first': True,
        'kelly_state': parsed_state,
        'external_events': external_events,
        'significance_result': significance_result,
        'conversation_check': conversation_check,
        'recent_activity': recent_activity,
        'candidate_messages': candidates,
        'recent_log_count_72h': len(recent_log),
        'hours_since_last_meaningful_send': last_meaningful_send_hours(recent_log),
    }
    _ensure_parent(PROACTIVE_STATE_FILE)
    with open(PROACTIVE_STATE_FILE, 'w') as f:
        json.dump(snapshot, f, indent=2)
    return snapshot


def _message_mode_from_source(source: str) -> str:
    mapping = {
        'significance': 'emotional_follow_up',
        'run': 'body_training_read',
        'health': 'body_training_read',
        'pattern': 'pattern_notice',
        'assist': 'practical_assist',
    }
    return mapping.get(source, 'pattern_notice')


def evaluate_snapshot(snapshot: Dict[str, object]) -> Dict[str, object]:
    recent_activity = snapshot.get('recent_activity', {}) or {}
    if recent_activity.get('recent_activity'):
        return {
            'decision': 'suppress',
            'reason': 'recent-active-conversation',
            'why_now': 'Kelly is already actively engaged; do not interrupt with proactive output.',
            'message': '',
            'message_mode': '',
            'confidence': 0.0,
            'quality_gate': 'not-run',
        }

    if recent_activity.get('negative_sentiment'):
        return {
            'decision': 'suppress',
            'reason': 'recent-negative-sentiment',
            'why_now': 'Recent conversation tone looks negative or loaded; stay quiet unless a stronger follow-up exists.',
            'message': '',
            'message_mode': '',
            'confidence': 0.0,
            'quality_gate': 'not-run',
        }

    candidates = snapshot.get('candidate_messages', []) or []
    for candidate in candidates:
        message = (candidate.get('message') or '').strip()
        if not message:
            continue
        allowed, reason = validate_proactive_message(message)
        if not allowed:
            continue

        source = candidate.get('source', 'pattern')
        return {
            'decision': 'send',
            'reason': source,
            'why_now': candidate.get('why_now') or 'Meaningful proactive signal detected.',
            'message': message,
            'message_mode': candidate.get('message_mode') or _message_mode_from_source(source),
            'confidence': candidate.get('confidence', 0.78),
            'quality_gate': reason,
        }

    return {
        'decision': 'suppress',
        'reason': 'no-strong-candidate',
        'why_now': 'No candidate passed the proactive quality bar.',
        'message': '',
        'message_mode': '',
        'confidence': 0.0,
        'quality_gate': 'none-passed',
    }


def log_decision(snapshot: Dict[str, object], decision: Dict[str, object]) -> None:
    _ensure_parent(PROACTIVE_LOG_FILE)
    record = {
        'timestamp': snapshot.get('timestamp') or datetime.now().isoformat(timespec='seconds'),
        'decision': decision.get('decision'),
        'reason': decision.get('reason'),
        'message_mode': decision.get('message_mode'),
        'confidence': decision.get('confidence'),
        'quality_gate': decision.get('quality_gate'),
        'why_now': decision.get('why_now'),
        'message': decision.get('message'),
        'hours_since_last_meaningful_send': snapshot.get('hours_since_last_meaningful_send'),
        'recent_log_count_72h': snapshot.get('recent_log_count_72h'),
        'candidate_count': len(snapshot.get('candidate_messages', []) or []),
    }
    with open(PROACTIVE_LOG_FILE, 'a') as f:
        f.write(json.dumps(record) + "\n")


__all__ = [
    'PROACTIVE_LOG_FILE',
    'PROACTIVE_STATE_FILE',
    'build_snapshot',
    'evaluate_snapshot',
    'log_decision',
    'parse_compact_kelly_state',
]

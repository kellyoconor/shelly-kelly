#!/usr/bin/env python3
"""
Conservative follow-up extractor.
Turns meaningful conversation summaries into structured follow-ups only when the text clearly implies an unresolved loop.
"""

import importlib.util
import json
import pathlib
import re
import sys

MODULE_PATH = pathlib.Path('/data/workspace/scripts/kelly-followups.py')
spec = importlib.util.spec_from_file_location('kelly_followups', MODULE_PATH)
kelly_followups = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kelly_followups)
add_followup = kelly_followups.add_followup

NOISE_PATTERNS = [
    'heartbeat',
    'gateway connected',
    'gateway disconnected',
    'whatsapp gateway',
    'no urgent issues',
    'no new urgent alerts',
]

FOLLOWUP_RULES = [
    {
        'pattern': r'follow up on (?P<topic>.+)',
        'kind': 'general',
        'priority': 'medium',
    },
    {
        'pattern': r'reminder about (?P<topic>.+)',
        'kind': 'practical',
        'priority': 'medium',
    },
    {
        'pattern': r'conflicted about (?P<topic>.+)',
        'kind': 'decision',
        'priority': 'high',
    },
    {
        'pattern': r'deciding whether to (?P<topic>.+)',
        'kind': 'decision',
        'priority': 'high',
    },
    {
        'pattern': r'asked to remember (?P<topic>.+)',
        'kind': 'general',
        'priority': 'high',
    },
    {
        'pattern': r'needs follow-up on (?P<topic>.+)',
        'kind': 'general',
        'priority': 'high',
    },
]


def normalize_topic(topic):
    topic = re.sub(r'[\.;,]+$', '', topic.strip())
    return topic[:160]


def extract_followup(summary):
    if not summary or not summary.strip():
        return None

    lowered = summary.lower()
    if any(pattern in lowered for pattern in NOISE_PATTERNS):
        return None

    for rule in FOLLOWUP_RULES:
        match = re.search(rule['pattern'], summary, re.I)
        if match:
            topic = normalize_topic(match.group('topic'))
            if not topic:
                return None
            return {
                'topic': topic,
                'note': summary.strip(),
                'kind': rule['kind'],
                'priority': rule['priority'],
            }

    return None


def main():
    if len(sys.argv) < 2:
        print('Usage: followup-extractor.py <summary text> [--apply]')
        return 1

    apply_mode = '--apply' in sys.argv[1:]
    args = [arg for arg in sys.argv[1:] if arg != '--apply']
    summary = ' '.join(args).strip()

    result = extract_followup(summary)
    if not result:
        print('{}')
        return 0

    if apply_mode:
        created = add_followup(
            result['topic'],
            result['note'],
            result['kind'],
            result['priority'],
        )
        print(json.dumps(created, indent=2))
        return 0

    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

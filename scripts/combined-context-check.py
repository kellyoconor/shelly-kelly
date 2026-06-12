#!/usr/bin/env python3
"""
Combined Context Checker
Runs both full context check (Strava, Oura, calendar) AND significance check (memory analysis)
Merges results intelligently to prioritize the most relevant check-in

Supports --daily-note-mode to auto-append significant events to vault daily notes
"""

import fcntl
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

try:
    from message_quality_gate import validate_proactive_message
except ModuleNotFoundError:  # pragma: no cover - import path differs in module tests
    from scripts.message_quality_gate import validate_proactive_message

try:
    from proactive_presence import build_snapshot, evaluate_snapshot, log_decision
except ModuleNotFoundError:  # pragma: no cover - import path differs in module tests
    from scripts.proactive_presence import build_snapshot, evaluate_snapshot, log_decision

LOCK_PATH = "/tmp/combined-context-check.lock"
FULL_CONTEXT_TIMEOUT = 8
SIGNIFICANCE_TIMEOUT = 4
APPEND_TIMEOUT = 6


@contextmanager
def single_instance_lock(lock_path):
    lock_file = open(lock_path, 'w')
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield True
    except BlockingIOError:
        yield False
    finally:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
        except Exception:
            pass
        lock_file.close()


def run_command(cmd, cwd=None, timeout=FULL_CONTEXT_TIMEOUT):
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None


def run_full_context_check():
    """Get external data context (Strava, Oura, calendar)."""
    fixture_path = os.environ.get('COMBINED_CONTEXT_EXTERNAL_FIXTURE')
    if fixture_path:
        try:
            with open(fixture_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"error": "External fixture load failed"}

    result = run_command(
        ['python3', '/data/workspace/scripts/full-context-check.py'],
        cwd='/data/workspace',
        timeout=FULL_CONTEXT_TIMEOUT,
    )

    if result is None:
        return {"error": "Full context check timed out"}
    if result.returncode != 0:
        return {"error": "Full context check failed"}

    output = result.stdout
    external_events = {}

    if "✅ Ran today:" in output:
        run_line = [l for l in output.split('\n') if "✅ Ran today:" in l][0]
        external_events['run_today'] = run_line.replace('🏃‍♀️ Running: ', '')

    if "🔒 Calendar auth expired" in output:
        external_events['calendar_auth'] = "Calendar authentication expired"

    health_lines = [l for l in output.split('\n') if l.startswith('💍 Health:')]
    if health_lines:
        external_events['health'] = health_lines[0].replace('💍 Health: ', '')

    obsidian_lines = [l for l in output.split('\n') if l.startswith('📚 Obsidian:')]
    if obsidian_lines:
        external_events['obsidian'] = obsidian_lines[0].replace('📚 Obsidian: ', '')

    running_lines = [l for l in output.split('\n') if l.startswith('🏃‍♀️ Running:')]
    if running_lines:
        external_events['running'] = running_lines[0].replace('🏃‍♀️ Running: ', '')

    return external_events


def run_significance_check():
    """Get memory-based significance analysis."""
    fixture_path = os.environ.get('COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE')
    if fixture_path:
        try:
            with open(fixture_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {"error": "Significance fixture load failed"}

    result = run_command(
        ['python3', '/data/workspace/scripts/context-significance-check.py'],
        cwd='/data/workspace',
        timeout=SIGNIFICANCE_TIMEOUT,
    )

    if result is None:
        return {"error": "Significance check timed out"}
    if result.returncode == 0 and result.stdout.strip():
        return {"significance_message": result.stdout.strip()}
    if result.returncode == 0:
        return {"no_significance": True}
    return {"error": "Significance check failed"}


def check_recent_conversation():
    """Check if we've recently discussed activities to avoid repetition."""
    fixture = os.environ.get('COMBINED_CONTEXT_CONVERSATION_JSON')
    if fixture:
        try:
            return json.loads(fixture)
        except json.JSONDecodeError:
            return {
                'running': False,
                'health_data': False,
                'calendar': False,
                'current_work': False,
                'morning_routine': False,
            }

    try:
        session_state_file = "/data/workspace/memory/session-discussion-state.json"

        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            session_state = {}

        current_date = datetime.now().strftime("%Y-%m-%d")

        if 'discussed_topics' not in session_state:
            session_state = {
                'last_date': current_date,
                'discussed_topics': {
                    'running': False,
                    'health_data': False,
                    'calendar': False
                }
            }
        else:
            try:
                last_updated = session_state.get('last_updated')
                if last_updated:
                    last_update_time = datetime.fromisoformat(last_updated)
                    hours_since_update = (datetime.now() - last_update_time).total_seconds() / 3600
                    if hours_since_update > 4:
                        today = datetime.now().strftime("%Y-%m-%d")
                        update_date = last_update_time.strftime("%Y-%m-%d")
                        if today != update_date:
                            existing_topics = session_state.get('discussed_topics', {})
                            session_state['discussed_topics'] = {
                                'running': existing_topics.get('running', False),
                                'health_data': existing_topics.get('health_data', False),
                                'calendar': existing_topics.get('calendar', False),
                                'current_work': existing_topics.get('current_work', False),
                                'morning_routine': False
                            }
                            session_state['last_date'] = today
            except Exception:
                pass

        discussed_topics = session_state.get('discussed_topics', {
            'running': False,
            'health_data': False,
            'calendar': False
        })

        if not discussed_topics.get('running'):
            fallback = check_timestamp_fallback()
            discussed_topics['running'] = fallback.get('running', False)

        return discussed_topics
    except Exception:
        return check_timestamp_fallback()


def check_timestamp_fallback():
    """Fallback timestamp-based check when session history isn't available"""
    try:
        session_state_file = "/data/workspace/memory/session-discussion-state.json"
        session_topics = {}

        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
                session_topics = session_state.get('discussed_topics', {})
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        state_file = "/data/workspace/memory/context-check-history.json"
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}

        discussed_topics = {
            'running': session_topics.get('running', False),
            'health_data': session_topics.get('health_data', False),
            'calendar': session_topics.get('calendar', False),
            'current_work': session_topics.get('current_work', False),
            'morning_routine': session_topics.get('morning_routine', False)
        }

        if 'last_run_checkin' in state:
            last_checkin = datetime.fromisoformat(state['last_run_checkin'])
            cutoff = datetime.now() - timedelta(hours=2)
            if last_checkin > cutoff:
                discussed_topics['running'] = True

        return discussed_topics
    except Exception:
        return {
            'running': False,
            'health_data': False,
            'calendar': False,
            'conversation_unavailable': True
        }


def record_run_checkin():
    """Record that we just asked about running to avoid repetition"""
    try:
        state_file = "/data/workspace/memory/context-check-history.json"
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}

        state['last_run_checkin'] = datetime.now().isoformat()
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

        record_discussion_topic('running')
    except Exception:
        pass


def record_discussion_topic(topic):
    """Record that we discussed a specific topic in this session"""
    try:
        session_state_file = "/data/workspace/memory/session-discussion-state.json"
        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            session_state = {}

        if 'discussed_topics' not in session_state:
            session_state['discussed_topics'] = {}

        session_state['discussed_topics'][topic] = True
        session_state['last_updated'] = datetime.now().isoformat()

        with open(session_state_file, 'w') as f:
            json.dump(session_state, f, indent=2)
    except Exception:
        pass


def detect_and_record_response(user_message):
    """Detect what Kelly is responding to and mark appropriate topics as discussed"""
    try:
        message_lower = user_message.lower()
        detected_topics = []

        if any(phrase in message_lower for phrase in [
            'rest day', 'no run', "didn't run", "haven't run", 'not running',
            'ran ', 'going to run', 'will run', 'planning to run'
        ]):
            detected_topics.append('running')

        if any(phrase in message_lower for phrase in [
            'feeling', 'energy', 'tired', 'good', 'ok', 'fine', 'great',
            'exhausted', 'ready', 'sleep', 'rested'
        ]):
            detected_topics.append('health_data')

        if any(phrase in message_lower for phrase in [
            'coffee', 'starbucks', 'caffeine', 'morning', 'usual order',
            'hazelnut', 'vanilla', 'iced coffee'
        ]):
            detected_topics.append('morning_routine')

        if any(phrase in message_lower for phrase in [
            'steely', 'development', 'coding', 'working on', 'project',
            'breakthrough', 'progress'
        ]):
            detected_topics.append('current_work')

        if any(phrase in message_lower for phrase in [
            'calendar', 'auth', 'authentication', 'fix', 'broken'
        ]):
            detected_topics.append('calendar')

        for topic in detected_topics:
            record_discussion_topic(topic)

        return detected_topics
    except Exception:
        return []


def passes_quality_gate(message):
    """Require proactive messages to use the shared quality gate."""
    allowed, _reason = validate_proactive_message(message)
    return allowed


def build_run_message(run_info):
    """Create a higher-signal run message when there's something real to say."""
    if not run_info:
        return ''
    return (
        f"Nice work on your run — {run_info}. "
        "That usually means the day already has some momentum; protect that instead of negotiating with it."
    )


def build_health_message(health_msg, running_context):
    """Create a health/body read only when it adds actual synthesis."""
    if not health_msg:
        return ''

    health_lower = health_msg.lower()
    running_lower = (running_context or '').lower()

    if any(token in health_lower for token in ['😴', '🥱', '💤', 'sleep']) and 'yesterday' in running_lower:
        return (
            f"Your body data looks mixed today: {health_msg}. "
            "Because you already put work in yesterday, this feels more like a rhythm/protect-your-energy day than a prove-something day."
        )

    if any(token in health_lower for token in ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '💪', '🔥', '⚡']):
        return (
            f"Your body looks pretty available today: {health_msg}. "
            "That doesn't mean force it — just that structure will probably work better than hesitation."
        )

    return ''


def parse_kelly_state_sections(kelly_state_text):
    sections = {
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
        if normalized in sections:
            sections[normalized] = value.strip()
    return sections


def build_followup_message(open_loops_text, tone_text):
    if not open_loops_text:
        return ''
    loop_text = open_loops_text.replace('Open loops: ', '').strip()
    if not loop_text:
        return ''
    tone_clause = ''
    if tone_text:
        tone_clause = f" {tone_text}"
    return (
        f"You still have an open loop around {loop_text}.{tone_clause} "
        "Feels like this might be a good moment to close the gap instead of letting it keep humming in the background. Want me to help you force a next step?"
    )


def build_relational_silence_message(state_sections):
    tone = state_sections.get('tone', '')
    physical = state_sections.get('physical', '')
    focus = state_sections.get('focus', '')
    if not tone and not physical:
        return ''
    return (
        f"Quick read: {physical} {tone} {focus}".strip() +
        " I don't think this needs a big intervention — just a useful nudge to keep the day from getting away from you. Want me to turn that into a low-lift next step?"
    )


def build_project_assist_message(state_sections):
    focus = state_sections.get('focus', '')
    if 'Active project energy:' not in focus:
        return ''
    project = focus.replace('Active project energy:', '').strip()
    return (
        f"{project} still looks live right now. That usually means the hard part is not ideas, it's choosing the next clean move. "
        "If you want, I can turn the current project energy into a tiny concrete next-step list."
    )


def build_proactive_candidates(external_events, significance_result, conversation_check, kelly_state_text, hours_since_last_send=None):
    """Build ordered proactive candidates for the evaluator."""
    candidates = []
    state_sections = parse_kelly_state_sections(kelly_state_text)

    if 'significance_message' in significance_result:
        significance_message = significance_result['significance_message']
        if significance_message and significance_message.strip():
            candidates.append({
                'source': 'significance',
                'message_mode': 'emotional_follow_up',
                'message': significance_message,
                'why_now': 'Recent memory/context significance produced a message with actual substance.',
                'confidence': 0.86,
                'min_gap_hours': 1,
            })

    if 'run_today' in external_events and not conversation_check.get('running', False):
        run_message = build_run_message(external_events['run_today'])
        if run_message:
            candidates.append({
                'source': 'run',
                'message_mode': 'body_training_read',
                'message': run_message,
                'why_now': 'A recent run creates a clear momentum/protection angle right now.',
                'confidence': 0.8,
                'min_gap_hours': 4,
            })

    if 'health' in external_events and not conversation_check.get('health_data', False):
        health_message = build_health_message(
            external_events['health'],
            external_events.get('running', ''),
        )
        if health_message:
            candidates.append({
                'source': 'health',
                'message_mode': 'body_training_read',
                'message': health_message,
                'why_now': 'Body signal + recent rhythm created a useful synthesis rather than a metric dump.',
                'confidence': 0.78,
                'min_gap_hours': 4,
            })

    followup_message = build_followup_message(
        state_sections.get('open_loops', ''),
        state_sections.get('tone', ''),
    )
    if followup_message:
        candidates.append({
            'source': 'followup',
            'message_mode': 'emotional_follow_up',
            'message': followup_message,
            'why_now': 'An open loop is still live and deserves proactive follow-through.',
            'confidence': 0.84,
            'min_gap_hours': 1,
        })

    project_assist = build_project_assist_message(state_sections)
    if project_assist and (hours_since_last_send is not None and hours_since_last_send >= 8):
        candidates.append({
            'source': 'assist',
            'message_mode': 'practical_assist',
            'message': project_assist,
            'why_now': 'Active project energy can be turned into immediate practical help.',
            'confidence': 0.72,
            'min_gap_hours': 8,
        })

    relational_silence = build_relational_silence_message(state_sections)
    if relational_silence and (hours_since_last_send is not None and hours_since_last_send >= 12):
        candidates.append({
            'source': 'pattern',
            'message_mode': 'pattern_notice',
            'message': relational_silence,
            'why_now': 'Enough time has passed that a grounded read with substance is appropriate.',
            'confidence': 0.68,
            'min_gap_hours': 12,
        })

    return candidates


def check_recent_kelly_messages():
    """Check Kelly's last 3 messages for timing and sentiment."""
    fixture = os.environ.get('COMBINED_CONTEXT_RECENT_STATE_JSON')
    if fixture:
        try:
            return json.loads(fixture)
        except json.JSONDecodeError:
            return {"recent_activity": False, "negative_sentiment": False}

    try:
        vault_daily_path = f"/data/kelly-vault/01-Daily/2026/{datetime.now().strftime('%Y-%m-%d')}.md"
        try:
            with open(vault_daily_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            return {"recent_activity": True, "negative_sentiment": True}

        current_time = datetime.now()
        lines = content.split('\n')
        recent_kelly_activity = False
        negative_sentiment = False

        for line in lines:
            if '**' in line and ':' in line and 'Kelly' in line:
                try:
                    time_part = line.split('**')[1].split('**')[0]
                    if ':' in time_part:
                        hour, minute = time_part.split(':')
                        message_time = current_time.replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
                        if (current_time - message_time).total_seconds() < 1800:
                            recent_kelly_activity = True
                            line_lower = line.lower()
                            if any(word in line_lower for word in [
                                'noooo', 'crying', 'emojis', 'upset', 'sad', 'frustrated',
                                'angry', 'annoyed', 'tired', 'exhausted', 'stressed',
                                'worried', 'anxious', 'overwhelmed', 'disappointed'
                            ]):
                                negative_sentiment = True
                                break
                except (ValueError, IndexError):
                    continue

        return {
            "recent_activity": recent_kelly_activity,
            "negative_sentiment": negative_sentiment
        }
    except Exception:
        return {"recent_activity": True, "negative_sentiment": True}


def check_last_heartbeat_time():
    """Legacy hook retained for compatibility.

    Blanket heartbeat cooldowns are intentionally disabled here.
    Proactive spacing is now enforced per-candidate inside proactive_presence.py
    so strong signals can still break through without reopening update-channel noise.
    """
    return False


def record_heartbeat_message():
    """Record that we just sent a heartbeat message"""
    try:
        heartbeat_state_file = "/data/workspace/memory/heartbeat-state.json"
        state = {
            'last_heartbeat_message_time': datetime.now().isoformat(),
            'last_heartbeat_date': datetime.now().strftime('%Y-%m-%d')
        }
        with open(heartbeat_state_file, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def get_kelly_state_compact():
    """Load compact Kelly state so the proactive snapshot uses the same active context layer."""
    result = run_command(
        ['python3', '/data/workspace/scripts/kelly-state-check.py', 'compact'],
        cwd='/data/workspace',
        timeout=6,
    )
    if result is None or result.returncode != 0:
        return ''
    return result.stdout.strip()


def get_combined_context():
    """Run both checks, evaluate proactive candidates, and return the best message if any."""
    if check_last_heartbeat_time():
        return ""

    recent_activity = check_recent_kelly_messages()
    external_events = run_full_context_check()
    significance_result = run_significance_check()
    conversation_check = check_recent_conversation()
    kelly_state_text = get_kelly_state_compact()

    if "error" in external_events and "error" in significance_result:
        snapshot = build_snapshot(
            external_events=external_events,
            significance_result=significance_result,
            conversation_check=conversation_check,
            kelly_state_text=kelly_state_text,
            recent_activity=recent_activity,
            candidates=[],
        )
        decision = evaluate_snapshot(snapshot)
        log_decision(snapshot, decision)
        return ""

    snapshot_seed = build_snapshot(
        external_events=external_events,
        significance_result=significance_result,
        conversation_check=conversation_check,
        kelly_state_text=kelly_state_text,
        recent_activity=recent_activity,
        candidates=[],
    )
    candidates = build_proactive_candidates(
        external_events,
        significance_result,
        conversation_check,
        kelly_state_text,
        snapshot_seed.get('hours_since_last_meaningful_send'),
    )
    snapshot = build_snapshot(
        external_events=external_events,
        significance_result=significance_result,
        conversation_check=conversation_check,
        kelly_state_text=kelly_state_text,
        recent_activity=recent_activity,
        candidates=candidates,
    )
    decision = evaluate_snapshot(snapshot)
    log_decision(snapshot, decision)

    if decision.get('decision') != 'send':
        return ""

    result = (decision.get('message') or '').strip()
    if not result:
        return ""

    if decision.get('reason') == 'run':
        record_run_checkin()
    if decision.get('reason') == 'health':
        record_discussion_topic('health_data')

    record_heartbeat_message()
    return result


def detect_and_log_events():
    """Detect significant events and log them to daily vault note"""
    try:
        external_events = run_full_context_check()
        significance_result = run_significance_check()
        events_logged = []

        if 'run_today' in external_events:
            run_info = external_events['run_today']
            if "✅ Ran today:" in run_info:
                run_details = run_info.replace("✅ Ran today: ", "")
                log_content = f"Morning run completed: {run_details}, feeling strong"
                result = run_command(
                    ['python3', '/data/workspace/scripts/daily-note-append.py', log_content, 'Health'],
                    cwd='/data/workspace',
                    timeout=APPEND_TIMEOUT,
                )
                if result is not None and result.returncode == 0:
                    events_logged.append(f"Logged run: {run_details}")

        if 'health' in external_events:
            health_info = external_events['health']
            if any(indicator in health_info for indicator in ['😴', '🥱', '💪', 'trending']):
                log_content = f"Health insight: {health_info}"
                result = run_command(
                    ['python3', '/data/workspace/scripts/daily-note-append.py', log_content, 'Health'],
                    cwd='/data/workspace',
                    timeout=APPEND_TIMEOUT,
                )
                if result is not None and result.returncode == 0:
                    events_logged.append(f"Logged health: {health_info}")

        if 'significance_message' in significance_result and 'big_building_day' in significance_result['significance_message']:
            log_content = "Technical work session - system improvements and fixes"
            result = run_command(
                ['python3', '/data/workspace/scripts/daily-note-append.py', log_content, 'Events'],
                cwd='/data/workspace',
                timeout=APPEND_TIMEOUT,
            )
            if result is not None and result.returncode == 0:
                events_logged.append("Logged technical session")

        if events_logged:
            return f"Daily note updated: {', '.join(events_logged)}"
        return ""
    except Exception as e:
        return f"Daily note logging error: {str(e)[:50]}"


if __name__ == "__main__":
    with single_instance_lock(LOCK_PATH) as acquired:
        if not acquired:
            sys.exit(0)

        if len(sys.argv) > 1 and '--daily-note-mode' in sys.argv:
            result = detect_and_log_events()
            if result:
                print(result)
        else:
            result = get_combined_context()
            if result:
                print(result)

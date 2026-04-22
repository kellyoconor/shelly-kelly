#!/usr/bin/env python3
"""
Combined Context Checker
Runs both full context check (Strava, Oura, calendar) AND significance check (memory analysis)
Merges results intelligently to prioritize the most relevant check-in

Supports --daily-note-mode to auto-append significant events to vault daily notes
"""

import fcntl
import json
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

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
    """Get external data context (Strava, Oura, calendar)"""
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
    """Get memory-based significance analysis"""
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
    """Check if we've recently discussed activities to avoid repetition"""
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


def merge_contexts(external_events, significance_result):
    """SMART Priority Logic - prioritize most INTERESTING/ACTIONABLE context"""
    messages = []
    conversation_check = check_recent_conversation()

    if 'run_today' in external_events and not conversation_check.get('running', False):
        run_info = external_events['run_today']
        messages.append(f"Nice work on your run! {run_info} - how did it feel? 🏃‍♀️")
        record_run_checkin()
        return messages[0]

    eastern_offset = timedelta(hours=-4)
    now = datetime.now(timezone.utc).astimezone(timezone(eastern_offset))
    if (
        now.weekday() < 5 and
        9 <= now.hour <= 17 and
        'run_today' not in external_events and
        not conversation_check.get('running', False)
    ):
        running_context = external_events.get('running', '')
        if 'Yesterday:' in running_context:
            messages.append("No run today - taking a rest day or just haven't gotten out there yet? 🏃‍♀️")
        else:
            messages.append("No run today - how's your energy for getting out there later? 🏃‍♀️")
        record_discussion_topic('running')
        return messages[0]

    if 'significance_message' in significance_result:
        messages.append(significance_result['significance_message'])
        return messages[0]

    if 9 <= now.hour <= 11 and not conversation_check.get('morning_routine', False):
        messages.append("Did you get your usual Starbucks order this morning? ☕")
        record_discussion_topic('morning_routine')
        return messages[0]

    obsidian_context = external_events.get('obsidian', '')
    if 'Steely' in obsidian_context and not conversation_check.get('current_work', False):
        messages.append("How's the Steely development going? Any breakthroughs today? 🤖")
        record_discussion_topic('current_work')
        return messages[0]

    if 'health' in external_events and not conversation_check.get('health_data', False):
        health_msg = external_events['health']
        if (
            any(emoji in health_msg for emoji in ['💪', '🔥', '⚡', '😴', '🥱', '💤']) or
            any(num in health_msg for num in ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100']) or
            any(num in health_msg for num in ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50'])
        ):
            if '😴' in health_msg or '🥱' in health_msg:
                messages.append(f"Your body's telling a story today: {health_msg}. How are you feeling energy-wise?")
            else:
                messages.append(f"Looking strong: {health_msg}. How's your energy matching the data?")
            record_discussion_topic('health_data')
            return messages[0]

    return messages[0] if messages else ""


def check_recent_kelly_messages():
    """Check Kelly's last 3 messages for timing and sentiment"""
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
    """Check if we sent a heartbeat message in the last 6 hours"""
    try:
        heartbeat_state_file = "/data/workspace/memory/heartbeat-state.json"
        try:
            with open(heartbeat_state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return False

        last_heartbeat = state.get('last_heartbeat_message_time')
        if not last_heartbeat:
            return False

        last_time = datetime.fromisoformat(last_heartbeat)
        hours_since = (datetime.now() - last_time).total_seconds() / 3600
        return hours_since < 6
    except Exception:
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


def get_combined_context():
    """Run both checks and return the most appropriate message"""
    if check_last_heartbeat_time():
        return ""

    kelly_state = check_recent_kelly_messages()
    if kelly_state.get("recent_activity", False):
        return ""
    if kelly_state.get("negative_sentiment", False):
        return ""

    external_events = run_full_context_check()
    significance_result = run_significance_check()

    if "error" in external_events and "error" in significance_result:
        return ""

    if "error" in external_events:
        if 'significance_message' in significance_result:
            result = significance_result['significance_message']
            record_heartbeat_message()
            return result
        return ""

    if "error" in significance_result:
        conversation_check = check_recent_conversation()
        if 'run_today' in external_events and not conversation_check.get('running', False):
            run_info = external_events['run_today']
            record_run_checkin()
            result = f"Saw your run! {run_info} - how did it feel? 🏃‍♀️"
            record_heartbeat_message()
            return result
        return ""

    result = merge_contexts(external_events, significance_result)
    if result and result.strip():
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

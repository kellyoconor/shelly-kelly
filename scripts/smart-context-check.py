#!/usr/bin/env python3
"""
Smart context checking before asking questions
Check available data sources before making assumptions
"""

import fcntl
import json
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timedelta

LOCK_PATH = "/tmp/smart-context-check.lock"
FULL_CONTEXT_TIMEOUT = 8
STRAVA_TIMEOUT = 6


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


def check_recent_runs(days_back=3):
    """Check if Kelly has run recently before asking about running"""
    result = run_command(
        ['python3', '/data/workspace/skills/strava/scripts/strava.py', 'runs', '5'],
        cwd='/data/workspace/skills/strava',
        timeout=STRAVA_TIMEOUT,
    )

    if result is None:
        return {"error": "Strava check timed out"}
    if result.returncode != 0:
        return {"error": "Could not check Strava"}

    try:
        runs = json.loads(result.stdout)
        recent_cutoff = datetime.now() - timedelta(days=days_back)

        recent_runs = []
        for run in runs:
            run_date = datetime.strptime(run['_date'], '%Y-%m-%d')
            if run_date >= recent_cutoff:
                recent_runs.append({
                    "date": run['_date'],
                    "distance": run['_distance_mi'],
                    "pace": run['_pace_mi'],
                    "location": "Jacksonville" if run['_date'] in ['2026-03-14', '2026-03-13'] else "Unknown"
                })

        recent_runs.sort(key=lambda x: x['date'], reverse=True)
        return {"recent_runs": recent_runs}
    except Exception as e:
        return {"error": f"Strava check failed: {e}"}


def should_ask_about_running():
    """Determine if it's appropriate to ask about running based on data"""
    runs_data = check_recent_runs(days_back=3)

    if "error" in runs_data:
        return True, "Could not check Strava, asking is OK"

    recent_runs = runs_data["recent_runs"]
    today = datetime.now().strftime('%Y-%m-%d')

    today_runs = [r for r in recent_runs if r["date"] == today]
    if today_runs:
        return True, f"Ran today: {today_runs[0]['distance']}mi at {today_runs[0]['pace']}"

    if recent_runs:
        last_run = recent_runs[0]
        days_since = (datetime.now() - datetime.strptime(last_run["date"], '%Y-%m-%d')).days
        return False, f"Last run: {last_run['date']} ({days_since} days ago), {last_run['distance']}mi at {last_run['pace']}"

    return True, "No recent runs found, asking about plans is OK"


def get_daily_context_summary():
    """Get full context summary before any conversation"""
    result = run_command(
        ['python3', '/data/workspace/scripts/full-context-check.py'],
        cwd='/data/workspace',
        timeout=FULL_CONTEXT_TIMEOUT,
    )

    if result is not None and result.returncode == 0:
        lines = result.stdout.split('\n')
        context_lines = [l for l in lines if l.startswith(('🏃‍♀️', '📅', '💍', '📚', '🔬', '📧'))]

        context = {}
        for line in context_lines:
            if '🏃‍♀️' in line:
                should_ask = not ('❌' in line or 'No recent' in line)
                context['running'] = {
                    'should_ask': should_ask,
                    'context': line.replace('🏃‍♀️ Running: ', '')
                }
            elif '📅' in line:
                context['calendar'] = line.replace('📅 Calendar: ', '')
            elif '💍' in line:
                context['health'] = line.replace('💍 Health: ', '')
            elif '📚' in line:
                context['obsidian'] = line.replace('📚 Obsidian: ', '')
            elif '🔬' in line:
                context['research'] = line.replace('🔬 Research: ', '')
            elif '📧' in line:
                context['email'] = line.replace('📧 Email: ', '')

        if context:
            return context

    should_ask_run, run_context = should_ask_about_running()
    fallback = {
        'running': {
            'should_ask': should_ask_run,
            'context': run_context
        }
    }
    if result is None:
        fallback['error'] = 'Context check timed out; using running-only fallback'
    elif result and result.returncode != 0:
        fallback['error'] = 'Context check failed; using running-only fallback'
    return fallback


def format_context_summary(context):
    """Format context for quick scanning"""
    lines = ["📊 CONTEXT CHECK BEFORE RESPONDING:"]

    if 'running' in context:
        run_info = context['running']
        status = "✅ Can ask" if run_info['should_ask'] else "❌ Don't ask"
        lines.append(f"🏃‍♀️ Running: {status} - {run_info['context']}")

    if 'calendar' in context:
        lines.append(f"📅 Calendar: {context['calendar']}")
    if 'health' in context:
        lines.append(f"💍 Health: {context['health']}")
    if 'obsidian' in context:
        lines.append(f"📚 Obsidian: {context['obsidian']}")
    if 'research' in context:
        lines.append(f"🔬 Research: {context['research']}")
    if 'email' in context:
        lines.append(f"📧 Email: {context['email']}")
    if 'error' in context:
        lines.append(f"⚠️ {context['error']}")

    return "\n".join(lines)


if __name__ == "__main__":
    with single_instance_lock(LOCK_PATH) as acquired:
        if not acquired:
            print("📊 CONTEXT CHECK BEFORE RESPONDING:")
            print("⚠️ smart-context-check already running; skipping duplicate run")
            sys.exit(0)

        if len(sys.argv) > 1 and sys.argv[1] == 'running':
            should_ask, context = should_ask_about_running()
            print(f"Should ask about running: {should_ask}")
            print(f"Context: {context}")
        else:
            context = get_daily_context_summary()
            print(format_context_summary(context))

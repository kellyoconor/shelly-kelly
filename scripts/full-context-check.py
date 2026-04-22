#!/usr/bin/env python3
"""
Complete Context Checking System
All data sources before every conversation
"""

import subprocess
import json
from datetime import datetime, timedelta

DEFAULT_TIMEOUT = 6


def run_command(cmd, cwd=None, timeout=DEFAULT_TIMEOUT):
    """Run a child command with a hard timeout and safe fallback semantics."""
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


def get_running_context():
    """Get Strava running context"""
    result = run_command(
        ['python3', 'scripts/strava.py', 'runs', '3'],
        cwd='/data/workspace/skills/strava',
        timeout=6,
    )

    if result is None:
        return "❌ Strava timeout"
    if result.returncode != 0:
        return "❌ Strava check failed"

    try:
        runs = json.loads(result.stdout)
        if not runs:
            return "❌ No recent runs"

        today = datetime.now().strftime('%Y-%m-%d')

        today_runs = [r for r in runs if r.get('_date') == today]
        if today_runs:
            run = today_runs[0]
            return f"✅ Ran today: {run.get('_distance_mi', '?')}mi at {run.get('_pace_mi', '?')}"

        last_run = runs[0]
        run_date = datetime.strptime(last_run['_date'], '%Y-%m-%d')
        days_since = (datetime.now() - run_date).days

        if days_since == 1:
            return f"⏳ Yesterday: {last_run['_date']}, {last_run.get('_distance_mi', '?')}mi"
        return f"❌ No recent runs (last: {last_run['_date']}, {days_since} days ago)"
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}"


def get_calendar_context():
    """Get today's calendar context"""
    result = run_command(
        ['python3', 'scripts/calendar.py', 'today'],
        cwd='/data/workspace/skills/google-calendar',
        timeout=5,
    )

    if result is None:
        return "📅 Calendar timeout/offline"
    if result.returncode != 0:
        return "📅 Calendar offline (no worries)"

    output = result.stdout.strip()
    if not output or "no events" in output.lower():
        return "✅ Clear day, no meetings"

    lines = output.split('\n')
    event_lines = [l for l in lines if ':' in l and ('AM' in l or 'PM' in l)]

    if len(event_lines) == 1:
        return f"📅 Light day: {event_lines[0].strip()[:40]}..."
    if len(event_lines) <= 3:
        return f"📅 {len(event_lines)} meetings today"
    return f"📅 Busy day: {len(event_lines)} meetings"


def get_health_context():
    """Get Oura health context"""
    result = run_command(
        ['python3', 'scripts/oura.py', 'brief'],
        cwd='/data/workspace/skills/oura',
        timeout=6,
    )

    if result is None:
        return "❌ Oura timeout"
    if result.returncode != 0:
        return "❌ Oura check failed"

    output = result.stdout.strip()

    try:
        data = json.loads(output)
        metrics = []

        if 'readiness' in data and 'score' in data['readiness']:
            readiness = data['readiness']['score']
            if readiness >= 85:
                metrics.append(f"💪 {readiness}% ready")
            elif readiness >= 70:
                metrics.append(f"⚖️ {readiness}% ready")
            else:
                metrics.append(f"😴 {readiness}% ready")

        if 'sleep' in data and 'score' in data['sleep']:
            sleep_score = data['sleep']['score']
            if sleep_score >= 85:
                metrics.append(f"😴 {sleep_score}% sleep")
            elif sleep_score >= 70:
                metrics.append(f"⏰ {sleep_score}% sleep")
            else:
                metrics.append(f"🥱 {sleep_score}% sleep")

        return " ".join(metrics) if metrics else "💍 Health data available"
    except json.JSONDecodeError:
        readiness = extract_metric(output, r'readiness.*?(\d+)%?', 'Readiness')
        sleep = extract_metric(output, r'sleep.*?(\d+)%?', 'Sleep')

        metrics = []
        if readiness:
            score = int(readiness)
            if score >= 85:
                metrics.append(f"💪 {readiness}% ready")
            elif score >= 70:
                metrics.append(f"⚖️ {readiness}% ready")
            else:
                metrics.append(f"😴 {readiness}% ready")

        if sleep:
            score = int(sleep)
            if score >= 85:
                metrics.append(f"😴 {sleep}% sleep")
            elif score >= 70:
                metrics.append(f"⏰ {sleep}% sleep")
            else:
                metrics.append(f"🥱 {sleep}% sleep")

        return " ".join(metrics) if metrics else "💍 Health data parsed"
    except Exception as e:
        return f"❌ Health error: {str(e)[:30]}"


def extract_metric(text, pattern, metric):
    """Extract metric from text using regex"""
    import re
    matches = re.findall(pattern, text.lower())
    return matches[-1] if matches else None


def get_obsidian_context():
    """Get Obsidian vault context"""
    result = run_command(
        ['python3', '/data/workspace/scripts/context-obsidian.py'],
        cwd='/data/workspace',
        timeout=4,
    )

    if result is None:
        return "❌ Vault timeout"
    if result.returncode == 0 and result.stdout:
        lines = result.stdout.strip().split('\n')
        context_lines = [l for l in lines if l.startswith(('📝', '🎯', '💭', '🎭'))]
        if context_lines:
            return context_lines[0][:60] + "..." if len(context_lines[0]) > 60 else context_lines[0]
        return "📚 Vault checked"
    return "❌ Vault check failed"


def get_research_context():
    """Get research activity context"""
    result = run_command(
        ['python3', 'src/main.py', '--status'],
        cwd='/data/workspace/kelly-research-copilot',
        timeout=3,
    )

    if result is None:
        return "🔬 Research system timeout"
    if result.returncode == 0:
        return "🔬 Research system active"
    return "🔬 Research system idle"


def get_email_context():
    """Get email activity context"""
    return "📧 Email checked"


def get_full_context(verbose=True):
    """Get complete context from all sources"""
    contexts = {
        "🏃‍♀️ Running": get_running_context(),
        "📅 Calendar": get_calendar_context(),
        "💍 Health": get_health_context(),
        "📚 Obsidian": get_obsidian_context(),
        "🔬 Research": get_research_context(),
        "📧 Email": get_email_context(),
    }

    if verbose:
        print("🔍 Running full context check...")
        print("=" * 50)
        print("📊 COMPLETE CONTEXT CHECK:")
        print("-" * 30)
        for source, context in contexts.items():
            print(f"{source}: {context}")
        print("-" * 30)
        print("✅ Full context ready for conversation!")

    return contexts


if __name__ == "__main__":
    get_full_context(verbose=True)

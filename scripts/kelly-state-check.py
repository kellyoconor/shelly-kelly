#!/usr/bin/env python3
"""
Kelly State Context System
Generate working memory about Kelly's current state
"""

import subprocess
import json
import os
import re
import sys
from datetime import datetime, timedelta

FOLLOWUPS_FILE = '/data/workspace/memory/kelly-followups.json'

def get_running_state():
    """Get Kelly's running state as natural knowledge"""
    try:
        result = subprocess.run(['python3', 'scripts/strava.py', 'runs', '3'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/strava')
        
        if result.returncode != 0:
            return "Kelly's running data is not available right now."
        
        runs = json.loads(result.stdout)
        if not runs:
            return "Kelly hasn't logged any recent runs."
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if run today
        today_runs = [r for r in runs if r['_date'] == today]
        if today_runs:
            run = today_runs[0]
            distance = run['_distance_mi']
            pace = run['_pace_mi']
            return f"Kelly ran {distance} miles today at a {pace} pace."
        
        # Check recent runs
        last_run = runs[0]
        run_date = datetime.strptime(last_run['_date'], '%Y-%m-%d')
        days_since = (datetime.now() - run_date).days
        
        if days_since == 0:
            return f"Kelly ran {last_run['_distance_mi']} miles today."
        elif days_since == 1:
            return f"Kelly ran {last_run['_distance_mi']} miles yesterday."
        elif days_since == 2:
            return f"Kelly last ran on {last_run['_date']} (2 days ago)."
        else:
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            run_weekday = weekdays[run_date.weekday()]
            return f"Kelly hasn't run since {run_weekday}, {last_run['_date']}."
            
    except Exception as e:
        return "Kelly's running data is not available right now."

def get_calendar_state():
    """Get Kelly's calendar state as natural knowledge"""
    try:
        result = subprocess.run(['python3', 'scripts/calendar.py', 'today'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/google-calendar')
        
        if result.returncode != 0:
            if "401" in result.stderr or "Unauthorized" in result.stderr:
                return "Kelly's calendar authentication has expired."
            else:
                return "Kelly's calendar information is not available."
        
        output = result.stdout.strip()
        if not output or "no events" in output.lower():
            return "Kelly has no meetings or events scheduled today."
        
        # Count events
        lines = output.split('\n')
        event_lines = [l for l in lines if ':' in l and ('AM' in l or 'PM' in l)]
        
        if len(event_lines) == 1:
            return "Kelly has one meeting scheduled today."
        elif len(event_lines) <= 3:
            return f"Kelly has {len(event_lines)} meetings scheduled today."
        else:
            return f"Kelly has a busy day with {len(event_lines)} meetings scheduled."
            
    except Exception as e:
        return "Kelly's calendar information is not available."

def get_health_state():
    """Get Kelly's health state as natural knowledge"""
    try:
        result = subprocess.run(['python3', 'scripts/oura.py', 'brief'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/oura')
        
        if result.returncode != 0:
            return "Kelly's health data is not available right now."
        
        output = result.stdout.strip()
        
        try:
            data = json.loads(output)
            
            states = []
            
            # Readiness score
            if 'readiness' in data and 'score' in data['readiness']:
                readiness = data['readiness']['score']
                if readiness >= 85:
                    states.append(f"Kelly's readiness is high at {readiness}%")
                elif readiness >= 70:
                    states.append(f"Kelly's readiness is moderate at {readiness}%")
                else:
                    states.append(f"Kelly's readiness is low at {readiness}%")
            
            # Sleep score
            if 'sleep' in data and 'score' in data['sleep']:
                sleep_score = data['sleep']['score']
                if sleep_score >= 85:
                    states.append(f"her sleep quality was excellent last night ({sleep_score}%)")
                elif sleep_score >= 70:
                    states.append(f"her sleep quality was decent last night ({sleep_score}%)")
                else:
                    states.append(f"her sleep was restless last night ({sleep_score}%)")
            
            if len(states) == 2:
                return f"{states[0]} and {states[1]}."
            elif len(states) == 1:
                return f"{states[0]}."
            else:
                return "Kelly's health metrics are available."
            
        except json.JSONDecodeError:
            return "Kelly's health data is available but not in expected format."
        
    except Exception as e:
        return "Kelly's health data is not available right now."

def get_obsidian_state():
    """Get Kelly's Obsidian vault activity as natural knowledge"""
    try:
        result = subprocess.run(['python3', '/data/workspace/scripts/context-obsidian.py'], 
                               capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0 and result.stdout:
            lines = result.stdout.strip().split('\n')
            
            # Look for activity indicators
            if any("no recent activity" in line.lower() for line in lines):
                return "Kelly hasn't been active in her vault recently."
            elif any("daily note" in line.lower() for line in lines):
                return "Kelly has been updating her daily notes."
            elif any("project" in line.lower() for line in lines):
                return "Kelly has been working on projects in her vault."
            else:
                return "Kelly has been writing in her vault."
        else:
            return "Kelly's vault activity is not available to check."
            
    except Exception as e:
        return "Kelly's vault activity is not available to check."

def get_research_state():
    """Get Kelly's research activity state"""
    try:
        result = subprocess.run(['python3', 'src/main.py', '--status'], 
                               capture_output=True, text=True, cwd='/data/workspace/kelly-research-copilot')
        
        if result.returncode == 0:
            return "Kelly's research system is monitoring in the background."
        else:
            return "Kelly's research system is idle."
            
    except Exception as e:
        return "Kelly's research system status is unknown."

def read_daily_note(date_obj):
    """Read a daily note from Kelly's vault if it exists."""
    path = f"/data/kelly-vault/01-Daily/2026/{date_obj.strftime('%Y-%m-%d')}.md"
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ''


def clean_note_bullet(text):
    """Strip markdown timestamp wrappers and excess formatting from note bullets."""
    cleaned = re.sub(r'^\*\*[^*]+\*\*:\s*', '', text.strip())
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()


def extract_bullets_from_section(content, section_name):
    """Pull simple bullets from a markdown section."""
    if not content:
        return []

    pattern = rf"## {re.escape(section_name)}\n(.*?)(?:\n## |\Z)"
    match = re.search(pattern, content, re.S)
    if not match:
        return []

    section = match.group(1)
    lines = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if line.startswith('- '):
            lines.append(clean_note_bullet(line[2:].strip()))
    return lines


def get_recent_daily_context():
    """Build a lightweight read of Kelly's recent rhythm from daily notes."""
    today_note = read_daily_note(datetime.now())
    yesterday_note = read_daily_note(datetime.now() - timedelta(days=1))

    notes = [today_note, yesterday_note]
    day_notes = []
    thoughts = []

    for note in notes:
        day_notes.extend(extract_bullets_from_section(note, 'Day Notes')[:2])
        thoughts.extend(extract_bullets_from_section(note, 'Thoughts')[:1])

    return {
        'day_notes': [item for item in day_notes if item][:3],
        'thoughts': [item for item in thoughts if item][:2],
    }


def parse_obsidian_summary():
    """Extract useful structured hints from the Obsidian summary output."""
    try:
        result = subprocess.run(
            ['python3', '/data/workspace/scripts/context-obsidian.py'],
            capture_output=True,
            text=True,
            cwd='/data/workspace',
        )
    except Exception:
        return {'active_projects': [], 'recent_focus': [], 'recent_mood': []}

    if result.returncode != 0 or not result.stdout:
        return {'active_projects': [], 'recent_focus': [], 'recent_mood': []}

    parsed = {'active_projects': [], 'recent_focus': [], 'recent_mood': []}
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith('🎯 Active projects:'):
            parsed['active_projects'] = [item.strip() for item in line.split(':', 1)[1].split(',') if item.strip()]
        elif line.startswith('📝 Recent focus:'):
            parsed['recent_focus'] = [item.strip() for item in line.split(':', 1)[1].split(',') if item.strip()]
        elif line.startswith('🎭 Recent mood:'):
            parsed['recent_mood'] = [item.strip() for item in line.split(':', 1)[1].split(',') if item.strip()]
    return parsed


def get_focus_state():
    """Determine what Kelly is currently focused on from recent notes, projects, and open loops."""
    context = get_recent_daily_context()
    obsidian = parse_obsidian_summary()
    open_loops = load_open_followups()

    if open_loops:
        top = open_loops[0]
        topic = top.get('topic', '').strip()
        kind = top.get('kind', '').strip()
        if topic:
            if kind == 'system':
                return f'Active build thread: {topic} is still live and wants follow-through.'
            return f'Open loop still in play: {topic}.'

    if obsidian['active_projects']:
        return f"Active project energy: {obsidian['active_projects'][0]} is live right now."

    if obsidian['recent_focus']:
        return f"Recent focus: {obsidian['recent_focus'][0]}."

    for item in context['day_notes']:
        lowered = item.lower()
        if 'run' in lowered or 'miles' in lowered:
            return 'Kelly has been in a training/body-awareness rhythm over the last couple of days.'
        if 'quiet' in lowered or 'low-drama' in lowered or 'reset' in lowered:
            return 'Kelly seems to be in a quieter reset rhythm right now, more about steadiness than chaos.'
        if 'project' in lowered or 'build' in lowered:
            return 'Kelly has active project energy right now, with some builder-mode momentum.'

    if context['thoughts']:
        return f"Recent theme: {context['thoughts'][0]}"

    vault_state = get_obsidian_state()
    if 'daily notes' in vault_state.lower():
        return 'Kelly has been actively reflecting in her daily notes.'
    if 'projects' in vault_state.lower():
        return 'Kelly has been spending energy on active projects.'

    return 'Kelly’s current focus is not fully clear from the latest context yet.'


def get_emotional_state():
    """Get lightweight emotional/rhythm context from recent notes."""
    context = get_recent_daily_context()
    obsidian = parse_obsidian_summary()

    for mood in obsidian['recent_mood']:
        lowered = mood.lower()
        if lowered == 'clear':
            return 'The recent tone looks clear and relatively grounded.'
        if lowered in ['frustrated', 'tired', 'overwhelmed', 'stressed', 'anxious', 'unclear']:
            return f'Recent mood signal: {lowered}.'

    for item in context['day_notes'] + context['thoughts']:
        lowered = item.lower()
        if 'quiet' in lowered or 'flat' in lowered:
            return 'The recent tone looks a little quiet/flat, even with decent body signals.'
        if 'resilient' in lowered or 'strong' in lowered:
            return 'There is a resilient undertone in the recent notes.'
        if 'pressure' in lowered:
            return 'Pressure has been part of the backdrop lately.'
    return ''


def load_open_followups():
    """Load unresolved follow-ups for active context."""
    try:
        with open(FOLLOWUPS_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    items = data.get('items', []) if isinstance(data, dict) else []
    return [item for item in items if item.get('status') == 'open']


def get_open_loops_state(limit=3):
    """Summarize current open loops in plain language."""
    items = load_open_followups()[:limit]
    if not items:
        return ''

    rendered = []
    for item in items:
        topic = item.get('topic', '').strip()
        note = item.get('note', '').strip()
        if topic and note:
            rendered.append(f"{topic}: {note}")
        elif topic:
            rendered.append(topic)

    if not rendered:
        return ''

    return 'Open loops: ' + ' | '.join(rendered)

def generate_kelly_state():
    """Generate Kelly State as natural working memory"""

    print("Kelly State:")
    print()

    # Physical state
    print("Physical:")
    running_state = get_running_state()
    health_state = get_health_state()
    print(f"- {running_state}")
    print(f"- {health_state}")
    print()

    # Schedule
    print("Schedule:")
    calendar_state = get_calendar_state()
    print(f"- {calendar_state}")
    print()

    # Activity
    print("Focus:")
    focus_state = get_focus_state()
    print(f"- {focus_state}")

    vault_state = get_obsidian_state()
    if "not available" not in vault_state:
        print(f"- {vault_state}")

    research_state = get_research_state()
    if "idle" not in research_state:
        print(f"- {research_state}")

    open_loops_state = get_open_loops_state()
    if open_loops_state:
        print(f"- {open_loops_state}")

    emotional_state = get_emotional_state()
    if emotional_state:
        print()
        print("Emotional:")
        print(f"- {emotional_state}")

def generate_compact_kelly_state():
    """Generate compact Kelly State for working memory injection"""

    running_state = get_running_state()
    health_state = get_health_state()
    calendar_state = get_calendar_state()
    focus_state = get_focus_state()
    emotional_state = get_emotional_state()
    open_loops_state = get_open_loops_state()

    state_lines = [
        f"Physical: {running_state} {health_state}",
        f"Schedule: {calendar_state}",
        f"Focus: {focus_state}"
    ]

    if emotional_state:
        state_lines.append(f"Tone: {emotional_state}")
    if open_loops_state:
        state_lines.append(open_loops_state)

    return "\n".join(state_lines)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'compact':
        print(generate_compact_kelly_state())
    else:
        generate_kelly_state()
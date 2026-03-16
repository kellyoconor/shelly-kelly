#!/usr/bin/env python3
"""
Kelly State Context System
Generate working memory about Kelly's current state
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timedelta

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

def get_focus_state():
    """Determine what Kelly is currently focused on"""
    # This could analyze recent vault activity, chat topics, etc.
    # For now, based on recent patterns from memory
    return "Kelly is currently focused on improving Shelly's architecture and context awareness."

def get_emotional_state():
    """Get background emotional context (from memory patterns)"""
    # This would analyze recent memory entries, vault notes, etc.
    # For now, placeholder based on known context
    return ""  # Only include if there's specific recent context

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
    
    # Emotional context (only if relevant)
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
    
    state_lines = [
        f"Physical: {running_state} {health_state}",
        f"Schedule: {calendar_state}",
        f"Focus: {focus_state}"
    ]
    
    return "\n".join(state_lines)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'compact':
        print(generate_compact_kelly_state())
    else:
        generate_kelly_state()
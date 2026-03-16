#!/usr/bin/env python3
"""
Smart context checking before asking questions
Check available data sources before making assumptions
"""

import subprocess
import json
import sys
from datetime import datetime, timedelta

def check_recent_runs(days_back=3):
    """Check if Kelly has run recently before asking about running"""
    try:
        result = subprocess.run([
            'python3', '/data/workspace/skills/strava/scripts/strava.py', 'runs', '5'
        ], capture_output=True, text=True, cwd='/data/workspace/skills/strava')
        
        if result.returncode != 0:
            return {"error": "Could not check Strava"}
        
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
        
        # Sort by date (most recent first)  
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
    
    # Check if run today
    today_runs = [r for r in recent_runs if r["date"] == today]
    if today_runs:
        return True, f"Ran today: {today_runs[0]['distance']}mi at {today_runs[0]['pace']}"
    
    # Check last run
    if recent_runs:
        last_run = recent_runs[0]  # Most recent
        days_since = (datetime.now() - datetime.strptime(last_run["date"], '%Y-%m-%d')).days
        return False, f"Last run: {last_run['date']} ({days_since} days ago), {last_run['distance']}mi at {last_run['pace']}"
    
    return True, "No recent runs found, asking about plans is OK"

def get_daily_context_summary():
    """Get full context summary before any conversation"""
    try:
        # Use the comprehensive context checker
        result = subprocess.run(['python3', '/data/workspace/scripts/full-context-check.py'], 
                              capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            # Parse the full context output
            lines = result.stdout.split('\n')
            context_lines = [l for l in lines if l.startswith(('🏃‍♀️', '📅', '💍', '📚', '🔬', '📧'))]
            
            context = {}
            for line in context_lines:
                if '🏃‍♀️' in line:
                    # Determine if should ask about running
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
            
            return context
        else:
            # Fallback to basic running check
            should_ask_run, run_context = should_ask_about_running()
            return {
                'running': {
                    'should_ask': should_ask_run,
                    'context': run_context
                }
            }
    except Exception as e:
        # Fallback to basic running check
        should_ask_run, run_context = should_ask_about_running()
        return {
            'running': {
                'should_ask': should_ask_run,
                'context': run_context
            },
            'error': f"Context check failed: {str(e)[:40]}"
        }

def format_context_summary(context):
    """Format context for quick scanning"""
    lines = ["📊 CONTEXT CHECK BEFORE RESPONDING:"]
    
    # Running
    if 'running' in context:
        run_info = context['running']
        status = "✅ Can ask" if run_info['should_ask'] else "❌ Don't ask"
        lines.append(f"🏃‍♀️ Running: {status} - {run_info['context']}")
    
    # Calendar
    if 'calendar' in context:
        lines.append(f"📅 Calendar: {context['calendar']}")
    
    # Health
    if 'health' in context:
        lines.append(f"💍 Health: {context['health']}")
    
    # Obsidian
    if 'obsidian' in context:
        lines.append(f"📚 Obsidian: {context['obsidian']}")
    
    # Research
    if 'research' in context:
        lines.append(f"🔬 Research: {context['research']}")
    
    # Email  
    if 'email' in context:
        lines.append(f"📧 Email: {context['email']}")
    
    # Error info
    if 'error' in context:
        lines.append(f"⚠️ {context['error']}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'running':
        # Just running check
        should_ask, context = should_ask_about_running()
        print(f"Should ask about running: {should_ask}")
        print(f"Context: {context}")
    else:
        # Full context summary
        context = get_daily_context_summary()
        print(format_context_summary(context))
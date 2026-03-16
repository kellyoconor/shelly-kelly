#!/usr/bin/env python3
"""
Smart context checking before asking questions
Check available data sources before making assumptions
"""

import subprocess
import json
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

if __name__ == "__main__":
    should_ask, context = should_ask_about_running()
    print(f"Should ask about running: {should_ask}")
    print(f"Context: {context}")
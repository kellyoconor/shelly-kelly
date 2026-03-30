#!/usr/bin/env python3
"""
Quick RPE Logger: Fast interface for post-run RPE capture

Usage: python3 rpe-quick-log.py [effort] [legs] [satisfaction] [notes]
Example: python3 rpe-quick-log.py 7 4 6 "felt sluggish but finished strong"
"""

import sys
import json
import subprocess
from datetime import datetime
from rpe_tracker import RPETracker

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 rpe-quick-log.py [effort 1-10] [legs 1-10] [satisfaction 1-10] [optional notes]")
        print("Example: python3 rpe-quick-log.py 7 4 6 'felt sluggish'")
        return
        
    try:
        perceived_effort = int(sys.argv[1])
        leg_feeling = int(sys.argv[2]) 
        satisfaction = int(sys.argv[3])
        notes = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        
        # Validate ranges
        if not all(1 <= x <= 10 for x in [perceived_effort, leg_feeling, satisfaction]):
            print("All ratings must be 1-10")
            return
            
    except ValueError:
        print("Error: effort, legs, and satisfaction must be numbers 1-10")
        return
    
    # Get today's run
    try:
        result = subprocess.run([
            'python3', '/data/workspace/skills/strava/scripts/strava.py', 'runs', '1'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            if runs and runs[0]['_date'] == datetime.now().strftime('%Y-%m-%d'):
                run = runs[0]
            else:
                print("No run found for today")
                return
        else:
            print("Error getting run data from Strava")
            return
            
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Log the RPE data
    tracker = RPETracker()
    tracker.capture_post_run_rpe(run, perceived_effort, leg_feeling, satisfaction, notes)
    
    print(f"✅ Logged RPE for {run['_distance_mi']}mi run:")
    print(f"   Effort: {perceived_effort}/10, Legs: {leg_feeling}/10, Satisfaction: {satisfaction}/10")
    if notes:
        print(f"   Notes: {notes}")
    
    # Quick analysis
    expected_effort = estimate_expected_effort(run.get('average_heartrate', 160))
    delta = perceived_effort - expected_effort
    
    if abs(delta) >= 2:
        if delta > 0:
            print(f"📊 Analysis: Felt {delta} points harder than HR suggests (possible fatigue)")
        else:
            print(f"📊 Analysis: Felt {abs(delta)} points easier than HR suggests (good recovery!)")

def estimate_expected_effort(avg_hr):
    """Quick effort estimate based on HR"""
    if not avg_hr:
        return 5
    if avg_hr < 150:
        return 3
    elif avg_hr < 160:
        return 5  
    elif avg_hr < 170:
        return 7
    else:
        return 9

if __name__ == "__main__":
    main()
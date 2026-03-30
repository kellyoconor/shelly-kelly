#!/usr/bin/env python3
"""
Post-Run Capture: Quick interface for logging perceived effort after runs

Usage: python3 post-run-capture.py
Automatically pulls today's Strava data and prompts for RPE ratings
"""

import subprocess
import json
import sys
from datetime import datetime
from rpe_tracker import RPETracker

def get_todays_run():
    """Get today's run from Strava"""
    try:
        result = subprocess.run([
            'python3', '/data/workspace/skills/strava/scripts/strava.py', 'runs', '1'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            if runs and runs[0]['_date'] == datetime.now().strftime('%Y-%m-%d'):
                return runs[0]
        return None
    except Exception as e:
        print(f"Error getting run data: {e}")
        return None

def prompt_rpe_data(run):
    """Interactive prompt for RPE data"""
    print(f"\n🏃‍♀️ Post-Run Check-in")
    print(f"Run: {run['_distance_mi']}mi at {run['_pace_mi']} pace")
    print(f"Avg HR: {run.get('average_heartrate', 'N/A')} bpm")
    print()
    
    try:
        # Perceived effort (1-10)
        print("How hard did this run FEEL? (1=very easy, 10=maximum effort)")
        perceived_effort = int(input("Perceived effort (1-10): "))
        
        # Leg feeling (1-10) 
        print("\nHow did your LEGS feel? (1=dead/heavy, 10=bouncy/strong)")
        leg_feeling = int(input("Leg feeling (1-10): "))
        
        # Overall satisfaction (1-10)
        print("\nOverall, how satisfied are you with this run? (1=terrible, 10=perfect)")
        satisfaction = int(input("Satisfaction (1-10): "))
        
        # Optional notes
        print("\nAny additional notes? (press enter to skip)")
        notes = input("Notes: ").strip()
        
        return {
            'perceived_effort': perceived_effort,
            'leg_feeling': leg_feeling,
            'satisfaction': satisfaction,
            'notes': notes
        }
        
    except (ValueError, KeyboardInterrupt):
        print("\nCancelled.")
        return None

def main():
    # Get today's run
    run = get_todays_run()
    if not run:
        print("No run found for today. Make sure you've synced Strava!")
        return
    
    # Get RPE data
    rpe_data = prompt_rpe_data(run)
    if not rpe_data:
        return
        
    # Save to Welly
    tracker = RPETracker()
    tracker.setup_rpe_tables()  # Ensure tables exist
    
    tracker.capture_post_run_rpe(
        run,
        rpe_data['perceived_effort'],
        rpe_data['leg_feeling'], 
        rpe_data['satisfaction'],
        rpe_data['notes']
    )
    
    print(f"\n✅ Logged RPE data for {run['_distance_mi']}mi run")
    
    # Show effort analysis
    effort_delta = rpe_data['perceived_effort'] - estimate_expected_effort(
        run.get('average_heartrate', 160), run['_pace_mi']
    )
    
    if abs(effort_delta) >= 2:
        if effort_delta > 0:
            print(f"📈 Note: Run felt {effort_delta} points harder than your HR suggests")
            print("   → Possible fatigue, poor sleep, or stress impact")
        else:
            print(f"📉 Note: Run felt {abs(effort_delta)} points easier than your HR suggests") 
            print("   → Good recovery or fitness improvement!")

def estimate_expected_effort(avg_hr, pace):
    """Quick estimate of expected effort (matches RPETracker logic)"""
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
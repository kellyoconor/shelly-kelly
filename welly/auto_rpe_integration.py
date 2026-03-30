#!/usr/bin/env python3
"""
Auto RPE Integration: Automatically detect and log RPE from Kelly's run responses

Monitors Kelly's responses to run questions and automatically extracts + logs RPE data
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from rpe_response_parser import auto_log_rpe_from_response

def get_recent_run():
    """Get today's run from Strava"""
    try:
        result = subprocess.run([
            'python3', '/data/workspace/skills/strava/scripts/strava.py', 'runs', '1'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            runs = json.loads(result.stdout)
            today = datetime.now().strftime('%Y-%m-%d')
            # Check if run is from today or yesterday (in case late logging)
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if runs and runs[0]['_date'] in [today, yesterday]:
                return runs[0]
        return None
    except Exception as e:
        print(f"Error getting run data: {e}")
        return None

def try_auto_rpe_log(response_text):
    """Try to automatically log RPE data from a response about running"""
    
    # Check if this looks like a response about running
    run_response_indicators = [
        'felt', 'feel', 'feeling', 'legs', 'hard', 'easy', 'tough', 'good', 
        'alright', 'okay', 'push', 'effort', 'tired', 'fresh', 'strong',
        'slow', 'fast', 'laggy', 'smooth', 'pace', 'hr', 'heart rate'
    ]
    
    response_lower = response_text.lower()
    if not any(indicator in response_lower for indicator in run_response_indicators):
        return None  # Doesn't look like a run response
        
    # Get recent run data
    run_data = get_recent_run()
    if not run_data:
        return None  # No recent run to associate with
        
    # Try to parse and log RPE
    result = auto_log_rpe_from_response(response_text, run_data)
    
    if result['logged']:
        # Log to daily note that we captured RPE
        try:
            subprocess.run([
                'python3', '/data/workspace/welly/welly-daily-writer.py',
                f"Auto-logged from natural response: {result['summary']}",
                'rpe'
            ], cwd='/data/workspace')
        except:
            pass  # Don't break if logging fails
            
        return {
            'success': True,
            'message': f"📊 {result['summary']}",
            'run_distance': run_data['_distance_mi'],
            'run_pace': run_data['_pace_mi']
        }
    else:
        return {
            'success': False,
            'reason': result['reason'],
            'confidence': result['data']['confidence']
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auto-rpe-integration.py 'response text'")
        sys.exit(1)
        
    response = " ".join(sys.argv[1:])
    result = try_auto_rpe_log(response)
    
    if result:
        if result['success']:
            print(f"✅ Auto-logged RPE data: {result['message']}")
        else:
            print(f"⚠️ Could not auto-log: {result['reason']}")
    else:
        print("ℹ️ Response doesn't appear to be about running")
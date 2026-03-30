#!/usr/bin/env python3
"""
Test RPE-Recovery Integration

Add some test RPE data to see if the integration correctly detects patterns
"""

import sqlite3
from datetime import datetime, timedelta
from rpe_tracker import RPETracker
import json

def add_test_rpe_data():
    """Add test RPE data that should trigger pattern detection"""
    
    # Create some runs that would normally have lower effort based on HR
    test_runs = [
        {
            'id': '999999991',
            '_date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
            '_distance_mi': 6.0,
            '_pace_mi': '8:45/mi',
            'average_heartrate': 160
        },
        {
            'id': '999999992', 
            '_date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            '_distance_mi': 5.5,
            '_pace_mi': '8:50/mi', 
            'average_heartrate': 158
        },
        {
            'id': '999999993',
            '_date': datetime.now().strftime('%Y-%m-%d'),
            '_distance_mi': 6.03,
            '_pace_mi': '8:56/mi',
            'average_heartrate': 165.8
        }
    ]
    
    # RPE data that shows consistently high effort despite reasonable HR
    test_rpe_data = [
        (8, 3, 4, "felt really hard despite moderate HR"),  # 2 days ago
        (8, 2, 4, "legs dead again, pushing through"),      # 1 day ago  
        (6, 2, 5, "still struggling but got through it")     # today (actual data)
    ]
    
    tracker = RPETracker()
    
    for i, (run_data, (effort, legs, satisfaction, notes)) in enumerate(zip(test_runs[:-1], test_rpe_data[:-1])):
        print(f"Adding test RPE data for {run_data['_date']}: Effort {effort}, Legs {legs}")
        tracker.capture_post_run_rpe(run_data, effort, legs, satisfaction, notes)
    
    print("Test data added!")

def test_integration():
    """Test the integrated recovery analysis"""
    from rpe_recovery_bridge import RPERecoveryBridge
    
    bridge = RPERecoveryBridge()
    state = bridge.check_and_update_recovery_state(days_back=5)
    
    print("\nIntegrated Recovery Analysis:")
    print(json.dumps(state, indent=2))
    
    if state['kelly_should_know']:
        print(f"\n🚨 Kelly should know: {state['kelly_message']}")
    else:
        print("\n✅ No immediate concerns detected")

if __name__ == "__main__":
    print("Testing RPE-Recovery Integration...")
    add_test_rpe_data() 
    test_integration()
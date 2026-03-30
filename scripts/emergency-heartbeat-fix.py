#!/usr/bin/env python3
"""
Emergency fix to prevent repetitive heartbeat messages
Records the last message sent and prevents identical messages within 4 hours
"""

import json
import os
from datetime import datetime, timedelta

def should_suppress_message(message):
    """Check if we should suppress this message due to recent repetition"""
    state_file = "/data/workspace/memory/last-heartbeat-message.json"
    
    try:
        # Load previous state
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
        else:
            state = {}
        
        # Check last message
        if 'last_message' in state and 'timestamp' in state:
            last_msg = state['last_message']
            last_time = datetime.fromisoformat(state['timestamp'])
            now = datetime.now()
            
            # If same message within 4 hours, suppress
            if (message.strip() == last_msg.strip() and 
                now - last_time < timedelta(hours=4)):
                return True
        
        # Record this message
        state['last_message'] = message.strip()
        state['timestamp'] = datetime.now().isoformat()
        
        # Save state
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        return False
        
    except Exception as e:
        # If anything fails, allow the message through
        return False

if __name__ == "__main__":
    import sys
    
    # Get the message that would be sent
    if len(sys.argv) > 1:
        message = sys.argv[1]
    else:
        # Get from combined context check
        import subprocess
        result = subprocess.run(['python3', '/data/workspace/scripts/combined-context-check.py'], 
                               capture_output=True, text=True, cwd='/data/workspace')
        message = result.stdout.strip()
    
    # Check if we should suppress
    if should_suppress_message(message):
        # Return empty (HEARTBEAT_OK equivalent)
        exit(0)
    else:
        # Return the message
        print(message)
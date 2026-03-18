#!/usr/bin/env python3
"""
Message Pipeline Interceptor
Intercepts messages to Kelly and auto-updates Kelly State first
"""

import subprocess
import sys
import os
import json
import time
from datetime import datetime

KELLY_NUMBER = "+[REDACTED_CLIENT_ID]401"
KELLY_STATE_UPDATE_SCRIPT = "/data/workspace/scripts/update-kelly-state.py"

def is_message_to_kelly(args):
    """Check if message is being sent to Kelly"""
    for i, arg in enumerate(args):
        if arg in ['--to', '--target']:
            if i + 1 < len(args) and args[i + 1] == KELLY_NUMBER:
                return True
    return False

def update_kelly_state():
    """Update Kelly State before messaging"""
    print(f"[{datetime.now()}] 🔄 Auto-updating Kelly State before message...")
    
    result = subprocess.run(['python3', KELLY_STATE_UPDATE_SCRIPT], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"[{datetime.now()}] ⚠️  Kelly State update failed: {result.stderr}")
    else:
        print(f"[{datetime.now()}] ✅ Kelly State updated successfully")
    
    return result.returncode == 0

def main():
    """Intercept openclaw message calls and add Kelly State update"""
    
    # Get the original command args (excluding this script)
    original_args = sys.argv[1:]
    
    # Check if this is a message to Kelly
    if 'message' in original_args and 'send' in original_args and is_message_to_kelly(original_args):
        print(f"[{datetime.now()}] 📡 Detected message to Kelly - activating context update...")
        update_kelly_state()
        time.sleep(1)  # Brief pause to ensure state file is written
    
    # Execute the original openclaw command
    cmd = ['openclaw'] + original_args
    result = subprocess.run(cmd, capture_output=False)
    
    return result.returncode

if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
Kelly State Pipeline Enforcer
Enforces fresh Kelly State before any message to Kelly
"""

import os
import time
from datetime import datetime, timedelta
import subprocess
import sys

KELLY_NUMBER = "+[REDACTED_CLIENT_ID]401"
KELLY_STATE_FILE = "/data/workspace/kelly-state.md"
KELLY_STATE_UPDATE_SCRIPT = "/data/workspace/scripts/update-kelly-state.py"

# Thresholds (in minutes)
PROACTIVE_ALWAYS_REFRESH = True  # Always refresh for proactive messages
STATE_EXPIRY_MINUTES = 20        # Refresh if older than this
RAPID_REPLY_GRACE_MINUTES = 5    # For back-and-forth conversations

def get_file_age_minutes(filepath):
    """Get age of file in minutes"""
    if not os.path.exists(filepath):
        return float('inf')  # Very old if doesn't exist
    
    mtime = os.path.getmtime(filepath)
    age_seconds = time.time() - mtime
    return age_seconds / 60

def is_kelly_state_fresh(is_proactive=True):
    """Check if Kelly State is fresh enough"""
    age_minutes = get_file_age_minutes(KELLY_STATE_FILE)
    
    if is_proactive and PROACTIVE_ALWAYS_REFRESH:
        return False  # Always refresh for proactive messages
    
    if age_minutes > STATE_EXPIRY_MINUTES:
        return False  # Too old, needs refresh
    
    if age_minutes <= RAPID_REPLY_GRACE_MINUTES:
        return True   # Fresh enough for rapid replies
    
    return False  # Default to refresh

def update_kelly_state():
    """Force update Kelly State"""
    print(f"🔄 [{datetime.now().strftime('%H:%M:%S')}] Refreshing Kelly State...")
    
    result = subprocess.run([sys.executable, KELLY_STATE_UPDATE_SCRIPT], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Kelly State update failed: {result.stderr}")
        return False
    
    print(f"✅ Kelly State refreshed")
    return True

def ensure_kelly_state(is_proactive=True):
    """Ensure Kelly State is fresh before messaging"""
    age_minutes = get_file_age_minutes(KELLY_STATE_FILE)
    
    if not is_kelly_state_fresh(is_proactive):
        if age_minutes < float('inf'):
            print(f"📊 Kelly State is {age_minutes:.1f} minutes old - refreshing...")
        else:
            print(f"📊 Kelly State missing - creating...")
        
        success = update_kelly_state()
        if not success:
            print("⚠️  Kelly State update failed, but proceeding...")
        
        return success
    else:
        print(f"📊 Kelly State is fresh ({age_minutes:.1f} min old) - using cached version")
        return True

def is_message_to_kelly(args):
    """Detect if this message is going to Kelly"""
    # Check for Kelly's number in various argument positions
    for i, arg in enumerate(args):
        if arg in ['--to', '--target'] and i + 1 < len(args):
            if args[i + 1] == KELLY_NUMBER:
                return True
        # Also check if Kelly's number appears anywhere (different arg formats)
        if KELLY_NUMBER in arg:
            return True
    
    return False

def detect_message_type(args):
    """Detect if this is proactive vs reactive message"""
    # For now, assume all messages are proactive unless we can detect otherwise
    # Could be enhanced to detect conversation context
    return True  # Proactive by default

def main():
    """Main enforcement function"""
    if len(sys.argv) < 2:
        print("Usage: kelly-state-enforcer.py <openclaw_message_args...>")
        return 1
    
    message_args = sys.argv[1:]
    
    # Check if this is a message to Kelly
    if not is_message_to_kelly(message_args):
        # Not a message to Kelly, pass through directly
        cmd = ['openclaw'] + message_args
        result = subprocess.run(cmd)
        return result.returncode
    
    # This IS a message to Kelly - enforce Kelly State
    is_proactive = detect_message_type(message_args)
    
    print(f"🎯 Message to Kelly detected ({'proactive' if is_proactive else 'reactive'})")
    
    # Ensure fresh Kelly State
    ensure_kelly_state(is_proactive)
    
    # Execute the original message command
    cmd = ['openclaw'] + message_args
    print(f"📤 Sending message with fresh context...")
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    exit(main())
#!/usr/bin/env python3
"""
AI Message Wrapper with Kelly State Enforcement
Automatically ensures Kelly State is fresh before any message to Kelly
"""

import subprocess
import sys
import os
from datetime import datetime

KELLY_NUMBER = "+13018302401"
KELLY_STATE_FILE = "/data/workspace/kelly-state.md"
KELLY_STATE_ENFORCER = "/data/workspace/scripts/kelly-state-enforcer.py"

def is_kelly_targeted(channel=None, to=None, target=None, **kwargs):
    """Check if message targets Kelly"""
    targets = [to, target]
    return any(t == KELLY_NUMBER for t in targets if t)

def enforce_kelly_state_for_ai():
    """AI-specific Kelly State enforcement"""
    print("🤖 AI Message Pipeline: Enforcing Kelly State...")
    
    # Always update for AI-initiated messages (they're usually proactive)
    result = subprocess.run([
        sys.executable, 
        "/data/workspace/scripts/update-kelly-state.py"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"⚠️ Kelly State update failed: {result.stderr}")
    else:
        print("✅ Kelly State updated for AI message")
    
    return result.returncode == 0

def load_kelly_state_context():
    """Ensure kelly-state.md is loaded as workspace context"""
    if os.path.exists(KELLY_STATE_FILE):
        with open(KELLY_STATE_FILE, 'r') as f:
            content = f.read()
        print("📖 Kelly State loaded as working memory context")
        return content
    else:
        print("⚠️ Kelly State file not found")
        return None

# Expose functions for AI tool usage
def prepare_kelly_message():
    """Prepare for sending message to Kelly - use this before message tool"""
    print("🔄 Preparing Kelly-aware message...")
    enforce_kelly_state_for_ai()
    kelly_state = load_kelly_state_context()
    return kelly_state

if __name__ == "__main__":
    # Command-line usage
    prepare_kelly_message()
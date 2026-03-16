#!/usr/bin/env python3
"""
Pre-response context check
Run this before any proactive message to Kelly
"""

import subprocess
import sys

def run_context_check():
    """Run the context check and display results"""
    print("🔍 Running mandatory context check...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            'python3', '/data/workspace/scripts/smart-context-check.py'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Context check failed: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error running context check: {e}")
    
    print("=" * 50)
    print("✅ Context check complete - use this info before responding!")

if __name__ == "__main__":
    run_context_check()
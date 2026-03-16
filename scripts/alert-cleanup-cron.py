#!/usr/bin/env python3
"""
Alert Cleanup Cron Job

Runs daily cleanup and reports results.
"""

import subprocess
import sys
import os

def run_cleanup():
    """Run the alert cleanup and return results"""
    try:
        # Run the cleanup script
        result = subprocess.run([
            sys.executable, 
            '/data/workspace/scripts/alert-cleanup.py'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            # Extract numbers from output
            output = result.stdout.strip()
            print(f"🧹 Daily alert cleanup completed!")
            print(f"📋 {output}")
            print(f"✅ Old resolved alerts cleared to prevent false wake-up alarms")
            return True
        else:
            print(f"❌ Alert cleanup failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running alert cleanup: {e}")
        return False

if __name__ == "__main__":
    success = run_cleanup()
    sys.exit(0 if success else 1)
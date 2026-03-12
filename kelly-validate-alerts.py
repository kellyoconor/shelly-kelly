#!/usr/bin/env python3
'''
KELLY'S ALERT SYSTEM VALIDATION SCRIPT

Use this to test that the alert system is truly fixed:

1. Run this script
2. Check if you receive the test alert on WhatsApp
3. Respond to it to confirm delivery works
4. Run validation again to confirm proper marking

This tests the ENTIRE delivery chain with REAL validation.
'''

import subprocess
import sys

def send_test_alert():
    print("📱 Sending test alert to Kelly via WhatsApp...")
    
    # Create a test alert
    result = subprocess.run([
        "python3", "/data/workspace/critical-alert-engine.py", "create",
        "🧪 REAL DELIVERY TEST - Kelly, please respond with 'test confirmed' when you receive this",
        "URGENT", "validation", "real-test"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        alert_id = result.stdout.split()[-1]
        print(f"✅ Test alert created: {alert_id}")
        print()
        print("📋 NEXT STEPS:")
        print("1. Check your WhatsApp for the test alert")
        print("2. Reply 'test confirmed' when you receive it")
        print(f"3. Run: python3 /data/workspace/critical-alert-engine.py respond {alert_id}")
        print("4. Check that it's properly marked as confirmed")
        print()
        print("If WhatsApp delivery fails, you should NOT receive anything,")
        print("and the system should NOT auto-mark it as delivered.")
        return alert_id
    else:
        print("❌ Failed to create test alert")
        return None

if __name__ == "__main__":
    print("🚨 KELLY'S ALERT SYSTEM VALIDATION")
    print("=" * 40)
    send_test_alert()
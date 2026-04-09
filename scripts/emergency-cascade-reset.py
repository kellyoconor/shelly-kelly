#!/usr/bin/env python3
"""
Emergency Cascade Reset Script
Use when system goes silent due to cron job cascade failures

Usage: python3 /data/workspace/scripts/emergency-cascade-reset.py
"""

import subprocess
import json
import sys
from datetime import datetime

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1

def check_cascade_risk():
    """Check if system is in cascade failure state"""
    print("🔍 Checking system health...")
    
    # Check session count
    stdout, stderr, code = run_command("openclaw status | grep sessions")
    if code == 0 and "sessions" in stdout:
        try:
            # Extract session count from status line
            session_count = int(stdout.split("sessions")[0].split()[-1])
            print(f"📊 Total sessions: {session_count}")
            
            if session_count > 60:
                print("🚨 CRITICAL: >60 sessions detected - cascade risk!")
                return True, session_count
            elif session_count > 30:
                print("⚠️  WARNING: >30 sessions detected - moderate risk")
                return True, session_count
            else:
                print("✅ Session count normal")
                return False, session_count
        except:
            print("❓ Could not parse session count")
            return False, 0
    else:
        print("❌ Could not check session status")
        return False, 0

def disable_problematic_jobs():
    """Temporarily disable messaging cron jobs to stop cascade"""
    print("\n🛑 Disabling problematic cron jobs...")
    
    # Jobs that commonly cause cascades when messaging fails
    risky_jobs = [
        "7cd3ead5-7eb0-48e8-b96f-300e302b707c",  # Emergency morning briefing
        "53bd0c03-b5ed-4941-9f63-e1af[REDACTED_CLIENT_ID]e81",  # Security review (sends WhatsApp)
    ]
    
    for job_id in risky_jobs:
        cmd = f"openclaw cron update {job_id} --enabled false"
        stdout, stderr, code = run_command(cmd)
        if code == 0:
            print(f"✅ Disabled job {job_id}")
        else:
            print(f"❌ Failed to disable job {job_id}: {stderr}")

def cleanup_stuck_sessions():
    """Force cleanup of old cron sessions"""
    print("\n🧹 Cleaning up stuck sessions...")
    
    cmd = "python3 /data/workspace/scripts/session-cleanup.py --force"
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print("✅ Session cleanup completed")
        print(stdout)
    else:
        print(f"❌ Session cleanup failed: {stderr}")

def test_whatsapp():
    """Test WhatsApp delivery"""
    print("\n📱 Testing WhatsApp delivery...")
    
    test_msg = f"🔧 Emergency reset completed at {datetime.now().strftime('%H:%M')} - system should be responsive again"
    cmd = f"""python3 -c "
from tools import message
result = message(action='send', channel='whatsapp', target='+[REDACTED_CLIENT_ID]401', message='{test_msg}')
print('WhatsApp test:', result)
" """
    
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print("✅ WhatsApp delivery test passed")
        return True
    else:
        print(f"❌ WhatsApp delivery test failed: {stderr}")
        return False

def main():
    """Main emergency reset procedure"""
    print("🚨 EMERGENCY CASCADE RESET STARTING")
    print("="*50)
    
    # 1. Check if we're in cascade state
    is_cascade, session_count = check_cascade_risk()
    
    # 2. If high risk, disable problematic jobs
    if is_cascade:
        disable_problematic_jobs()
        cleanup_stuck_sessions()
    
    # 3. Test WhatsApp connection
    whatsapp_ok = test_whatsapp()
    
    # 4. Summary
    print("\n" + "="*50)
    print("🏁 EMERGENCY RESET SUMMARY:")
    print(f"📊 Final session count: {session_count}")
    print(f"📱 WhatsApp delivery: {'✅ Working' if whatsapp_ok else '❌ Failed'}")
    
    if whatsapp_ok and session_count < 30:
        print("✅ System should be responsive again!")
        print("\nTo re-enable jobs later:")
        print("openclaw cron update 7cd3ead5-7eb0-48e8-b96f-300e302b707c --enabled true")
    else:
        print("⚠️  System may still need manual intervention")
        print("Consider restarting OpenClaw gateway: openclaw restart")

if __name__ == "__main__":
    main()
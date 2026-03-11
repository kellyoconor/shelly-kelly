#!/usr/bin/env python3
"""
Manual session management tool
Usage: python3 session-manager.py [audit|cleanup|emergency]
"""
import sys
import subprocess
import json
import os

def run_audit():
    """Run session audit"""
    print("🩺 Running session audit...")
    result = subprocess.run([
        "python3", "/data/workspace/scripts/session-audit.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def run_cleanup():
    """Run proper cleanup"""
    print("🧹 Running session cleanup...")
    result = subprocess.run([
        "python3", "/data/workspace/scripts/session-cleanup.py"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    return result.returncode == 0

def emergency_cleanup():
    """Emergency cleanup - removes ALL cron sessions regardless of age"""
    print("🚨 EMERGENCY CLEANUP - This will remove ALL cron sessions!")
    
    # Load registry
    sessions_json = "/data/.clawdbot/agents/main/sessions/sessions.json"
    try:
        with open(sessions_json, 'r') as f:
            registry = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load sessions.json: {e}")
        return False
    
    # Find all cron sessions
    cron_sessions = []
    for session_key, session_data in registry.items():
        if not session_key.startswith('session:'):
            continue
        
        label = session_data.get('label', '')
        if ('Cron:' in label or 
            'cron:' in session_key.lower() or 
            session_data.get('channel') == 'unknown'):
            cron_sessions.append(session_key)
    
    print(f"Found {len(cron_sessions)} cron sessions to delete")
    
    # Delete files and registry entries
    deleted = 0
    for session_key in cron_sessions:
        session_id = session_key.replace('session:', '')
        file_path = f"/data/.clawdbot/agents/main/sessions/{session_id}.jsonl"
        
        # Delete file if exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️  Deleted file: {session_id}")
            except Exception as e:
                print(f"❌ Failed to delete file {session_id}: {e}")
        
        # Remove from registry
        if session_key in registry:
            del registry[session_key]
            deleted += 1
    
    # Save updated registry
    try:
        # Backup first
        backup_path = f"{sessions_json}.emergency-backup-{int(__import__('time').time())}"
        subprocess.run(["cp", sessions_json, backup_path])
        
        with open(sessions_json, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"✅ Emergency cleanup complete: {deleted} sessions removed")
        print(f"Registry backup: {backup_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to save registry: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 session-manager.py [audit|cleanup|emergency]")
        print("  audit     - Show current session state")
        print("  cleanup   - Run proper cleanup (safe)")
        print("  emergency - Delete ALL cron sessions (use if system is broken)")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "audit":
        return 0 if run_audit() else 1
    elif command == "cleanup":
        return 0 if run_cleanup() else 1
    elif command == "emergency":
        response = input("Are you sure you want to delete ALL cron sessions? (yes/no): ")
        if response.lower() == "yes":
            return 0 if emergency_cleanup() else 1
        else:
            print("Emergency cleanup cancelled")
            return 0
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    exit(main())
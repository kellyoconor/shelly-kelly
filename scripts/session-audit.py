#!/usr/bin/env python3
"""
Audit current session state - shows what would be cleaned without doing it
"""
import json
import os
import glob
import time
from datetime import datetime, timedelta

SESSIONS_DIR = "/data/.clawdbot/agents/main/sessions"
SESSIONS_JSON = f"{SESSIONS_DIR}/sessions.json"

def load_session_registry():
    try:
        with open(SESSIONS_JSON, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load sessions.json: {e}")
        return None

def get_session_files():
    files = []
    pattern = f"{SESSIONS_DIR}/*.jsonl"
    
    for filepath in glob.glob(pattern):
        try:
            stat = os.stat(filepath)
            session_id = os.path.basename(filepath).replace('.jsonl', '')
            files.append({
                'path': filepath,
                'session_id': session_id,
                'modified': stat.st_mtime,
                'size': stat.st_size,
                'age_hours': (time.time() - stat.st_mtime) / 3600
            })
        except Exception as e:
            print(f"Warning: Could not stat {filepath}: {e}")
    
    return files

def is_cron_session(registry, session_id):
    session_key = f"session:{session_id}"
    session_data = registry.get(session_key, {})
    
    label = session_data.get('label', '')
    return ('Cron:' in label or 
            'cron:' in session_key.lower() or
            session_data.get('channel') == 'unknown')

def main():
    print("=== Session Audit ===")
    
    # Load registry
    registry = load_session_registry()
    if not registry:
        return
    
    # Get files
    session_files = get_session_files()
    
    print(f"\n📊 Current State:")
    print(f"   Session files: {len(session_files)}")
    registry_sessions = [k for k in registry.keys() if k.startswith('session:')]
    print(f"   Registry entries: {len(registry_sessions)}")
    
    # Analyze files
    cron_sessions = []
    regular_sessions = []
    orphaned_files = []
    
    for session_file in session_files:
        session_id = session_file['session_id']
        session_key = f"session:{session_id}"
        
        # Check if orphaned (file exists but no registry entry)
        if session_key not in registry:
            orphaned_files.append(session_file)
            continue
        
        if is_cron_session(registry, session_id):
            cron_sessions.append(session_file)
        else:
            regular_sessions.append(session_file)
    
    # Show what would be cleaned up
    print(f"\n🤖 Cron Sessions ({len(cron_sessions)}):")
    old_cron = [s for s in cron_sessions if s['age_hours'] > 1]
    for session in sorted(cron_sessions, key=lambda x: x['age_hours'], reverse=True):
        status = "🗑️ DELETE" if session['age_hours'] > 1 else "✅ KEEP"
        age = f"{session['age_hours']:.1f}h"
        size_kb = session['size'] // 1024
        session_data = registry.get(f"session:{session['session_id']}", {})
        label = session_data.get('label', 'unlabeled')
        print(f"   {status} {session['session_id'][:8]}... ({age}, {size_kb}KB) - {label}")
    
    print(f"\n👤 Regular Sessions ({len(regular_sessions)}):")
    old_regular = [s for s in regular_sessions if s['age_hours'] > 72]  # 3 days
    for session in sorted(regular_sessions, key=lambda x: x['age_hours'], reverse=True):
        status = "🗑️ DELETE" if session['age_hours'] > 72 else "✅ KEEP"
        age_days = session['age_hours'] / 24
        size_kb = session['size'] // 1024
        session_data = registry.get(f"session:{session['session_id']}", {})
        label = session_data.get('label', 'main session')
        print(f"   {status} {session['session_id'][:8]}... ({age_days:.1f}d, {size_kb}KB) - {label}")
    
    print(f"\n👻 Orphaned Files ({len(orphaned_files)}):")
    for session in orphaned_files:
        age_days = session['age_hours'] / 24
        size_kb = session['size'] // 1024
        print(f"   🗑️ DELETE {session['session_id'][:8]}... ({age_days:.1f}d, {size_kb}KB) - no registry entry")
    
    # Check for registry entries without files
    registry_without_files = []
    for session_key in registry_sessions:
        session_id = session_key.replace('session:', '')
        file_path = f"{SESSIONS_DIR}/{session_id}.jsonl"
        if not os.path.exists(file_path):
            registry_without_files.append(session_key)
    
    print(f"\n🔗 Registry Entries Without Files ({len(registry_without_files)}):")
    for entry in registry_without_files:
        session_data = registry[entry]
        label = session_data.get('label', 'unlabeled')
        print(f"   🧹 CLEAN {entry} - {label}")
    
    # Summary
    total_to_delete = len(old_cron) + len(old_regular) + len(orphaned_files)
    registry_to_clean = len(old_cron) + len(old_regular) + len(registry_without_files)
    
    print(f"\n📋 Cleanup Summary:")
    print(f"   Files to delete: {total_to_delete}")
    print(f"   Registry entries to remove: {registry_to_clean}")
    print(f"   Potential space saved: {sum(s['size'] for s in old_cron + old_regular + orphaned_files) // 1024} KB")

if __name__ == "__main__":
    main()
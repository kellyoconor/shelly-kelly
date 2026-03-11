#!/usr/bin/env python3
"""
Proper session cleanup for OpenClaw
Cleans both session files AND registry entries
"""
import json
import os
import glob
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SESSIONS_DIR = "/data/.clawdbot/agents/main/sessions"
SESSIONS_JSON = f"{SESSIONS_DIR}/sessions.json"
BACKUP_DIR = "/data/backups/vault-$(date +%Y%m%d)"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def backup_vault():
    """Backup vault before any cleanup"""
    log("Creating vault backup...")
    
    # Create backup directory
    backup_path = f"/data/backups/vault-{datetime.now().strftime('%Y%m%d')}.tar.gz"
    os.makedirs("/data/backups", exist_ok=True)
    
    # Use tar instead of rsync
    result = subprocess.run([
        "tar", "-czf", backup_path, "-C", "/data", "kelly-vault"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        log(f"✅ Vault backup complete: {backup_path}")
        return True
    else:
        log(f"❌ Vault backup failed: {result.stderr}")
        return False

def load_session_registry():
    """Load the current session registry"""
    try:
        with open(SESSIONS_JSON, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"❌ Failed to load sessions.json: {e}")
        return None

def save_session_registry(registry):
    """Save the updated session registry"""
    try:
        # Backup current registry first
        backup_path = f"{SESSIONS_JSON}.backup-{int(time.time())}"
        subprocess.run(["cp", SESSIONS_JSON, backup_path])
        
        with open(SESSIONS_JSON, 'w') as f:
            json.dump(registry, f, indent=2)
        
        log(f"✅ Updated session registry (backup at {backup_path})")
        return True
    except Exception as e:
        log(f"❌ Failed to save sessions.json: {e}")
        return False

def get_session_files():
    """Get all session .jsonl files with their timestamps"""
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
                'size': stat.st_size
            })
        except Exception as e:
            log(f"Warning: Could not stat {filepath}: {e}")
    
    return files

def is_cron_session(registry, session_id):
    """Check if a session is a cron session"""
    session_key = f"session:{session_id}"
    session_data = registry.get(session_key, {})
    
    # Check for cron indicators
    label = session_data.get('label', '')
    return ('Cron:' in label or 
            'cron:' in session_key.lower() or
            session_data.get('channel') == 'unknown')

def cleanup_sessions(max_age_hours=1, max_age_days_general=3):
    """
    Clean up old sessions
    - Cron sessions: delete after max_age_hours
    - General sessions: delete after max_age_days_general
    """
    log(f"Starting session cleanup (cron: {max_age_hours}h, general: {max_age_days_general}d)")
    
    # Load current registry
    registry = load_session_registry()
    if not registry:
        return False
    
    # Get all session files
    session_files = get_session_files()
    log(f"Found {len(session_files)} session files")
    
    # Calculate cutoff times
    now = time.time()
    cron_cutoff = now - (max_age_hours * 3600)
    general_cutoff = now - (max_age_days_general * 24 * 3600)
    
    deleted_files = 0
    deleted_registry_entries = 0
    
    # Process each session file
    for session_file in session_files:
        session_id = session_file['session_id']
        modified_time = session_file['modified']
        
        # Determine if this should be deleted
        should_delete = False
        reason = ""
        
        if is_cron_session(registry, session_id):
            if modified_time < cron_cutoff:
                should_delete = True
                reason = f"cron session older than {max_age_hours}h"
        else:
            if modified_time < general_cutoff:
                should_delete = True
                reason = f"general session older than {max_age_days_general}d"
        
        if should_delete:
            try:
                # Delete the file
                os.remove(session_file['path'])
                deleted_files += 1
                
                # Remove from registry
                session_key = f"session:{session_id}"
                if session_key in registry:
                    del registry[session_key]
                    deleted_registry_entries += 1
                
                log(f"🗑️  Deleted {session_id} ({reason})")
                
            except Exception as e:
                log(f"❌ Failed to delete {session_id}: {e}")
    
    # Save updated registry
    if deleted_registry_entries > 0:
        if save_session_registry(registry):
            log(f"✅ Registry updated: removed {deleted_registry_entries} entries")
        else:
            log("❌ Failed to update registry")
            return False
    
    # Clean up orphaned files (files without registry entries)
    orphaned = 0
    for session_file in session_files:
        session_id = session_file['session_id']
        session_key = f"session:{session_id}"
        
        if session_key not in registry and os.path.exists(session_file['path']):
            try:
                os.remove(session_file['path'])
                orphaned += 1
                log(f"🗑️  Deleted orphaned file {session_id}")
            except Exception as e:
                log(f"❌ Failed to delete orphaned file {session_id}: {e}")
    
    # Summary
    total_remaining = len(get_session_files())
    registry_size = len([k for k in registry.keys() if k.startswith('session:')])
    
    log(f"✅ Cleanup complete:")
    log(f"   Files deleted: {deleted_files}")
    log(f"   Registry entries removed: {deleted_registry_entries}")
    log(f"   Orphaned files cleaned: {orphaned}")
    log(f"   Remaining files: {total_remaining}")
    log(f"   Registry entries: {registry_size}")
    
    return True

def main():
    log("=== OpenClaw Session Cleanup ===")
    
    # Backup vault first
    if not backup_vault():
        log("❌ Aborting - vault backup failed")
        return 1
    
    # Run cleanup
    if cleanup_sessions():
        log("✅ Session cleanup successful")
        return 0
    else:
        log("❌ Session cleanup failed")
        return 1

if __name__ == "__main__":
    exit(main())
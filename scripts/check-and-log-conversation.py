#!/usr/bin/env python3
"""
Check and Log Conversation Summary

Called from heartbeat context where we know what conversation happened.
If meaningful conversation occurred, logs a simple summary to Activity Log.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def get_last_log_time():
    """Get when we last logged anything"""
    state_file = "/data/workspace/memory/conversation-log-state.json"
    
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_log_time', '2000-01-01T00:00:00'))
    except:
        pass
    
    return datetime(2000, 1, 1)

def save_log_time():
    """Record that we just logged something"""
    state_file = "/data/workspace/memory/conversation-log-state.json"
    
    try:
        data = {
            'last_log_time': datetime.now().isoformat(),
            'logged_today': datetime.now().strftime('%Y-%m-%d')
        }
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(data, f)
    except:
        pass

def should_log_now():
    """Check if enough time passed since last log"""
    last_log = get_last_log_time()
    time_since = datetime.now() - last_log
    
    # Only log if at least 15 minutes since last entry
    return time_since > timedelta(minutes=15)

def append_to_activity_log(summary: str) -> bool:
    """Append to Activity Log in vault daily note"""
    try:
        # Smart daily note detection - if it's early morning (before 6 AM), 
        # still log to yesterday's note as it's conceptually the same "day"
        current_time = datetime.now()
        if current_time.hour < 6:
            target_date = (current_time - timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            target_date = current_time.strftime('%Y-%m-%d')
            
        vault_daily_note = Path(f"/data/kelly-vault/01-Daily/2026/{target_date}.md")
        
        if not vault_daily_note.exists():
            # Try today's date as fallback
            fallback_date = current_time.strftime('%Y-%m-%d')
            vault_daily_note = Path(f"/data/kelly-vault/01-Daily/2026/{fallback_date}.md")
            if not vault_daily_note.exists():
                return False
        
        content = vault_daily_note.read_text()
        timestamp = datetime.now().strftime('%H:%M')
        entry = f"- **{timestamp}**: {summary}"
        
        # Add to Activity Log section
        if "## Activity Log" in content:
            section_start = content.find("## Activity Log")
            next_section = content.find("\n## ", section_start + 1)
            
            if next_section == -1:
                content = content.rstrip() + "\n" + entry + "\n"
            else:
                before_next = content[:next_section]
                after_next = content[next_section:]
                content = before_next.rstrip() + "\n" + entry + "\n\n" + after_next
        else:
            content = content.rstrip() + "\n\n## Activity Log\n" + entry + "\n"
        
        vault_daily_note.write_text(content)
        return True
        
    except:
        return False

def log_conversation(summary: str):
    """Log a conversation summary if appropriate"""
    if should_log_now():
        if append_to_activity_log(summary):
            save_log_time()
            return True
    return False

def main():
    """Log conversation if provided"""
    import sys
    
    if len(sys.argv) > 1:
        summary = ' '.join(sys.argv[1:])
        if log_conversation(summary):
            print(f"✅ Logged: {summary}")
        else:
            print("ℹ️  Too recent to log again")
    else:
        print("Usage: python3 check-and-log-conversation.py \"summary text\"")
    
    return 0

if __name__ == "__main__":
    exit(main())
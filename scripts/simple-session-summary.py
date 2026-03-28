#!/usr/bin/env python3
"""
Simple Session Summary for Daily Notes

Every heartbeat, if we had conversation in the last 30 minutes,
write a simple 1-3 sentence summary to the daily note.

No categories, no pattern matching, just "what did we talk about?"
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

def get_last_activity_timestamp():
    """Get the timestamp of when we last logged something"""
    state_file = "/data/workspace/memory/session-summary-state.json"
    
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
                return data.get('last_summary_time')
    except:
        pass
    
    return None

def save_activity_timestamp():
    """Save that we just logged something"""
    state_file = "/data/workspace/memory/session-summary-state.json"
    
    try:
        data = {
            'last_summary_time': datetime.now().isoformat()
        }
        with open(state_file, 'w') as f:
            json.dump(data, f)
    except:
        pass

def had_recent_conversation():
    """Check if we had meaningful conversation in the last 30 minutes"""
    # For now, simple check - if this script is being called, 
    # assume there might have been conversation worth summarizing
    
    last_logged = get_last_activity_timestamp()
    if not last_logged:
        return True  # First time running
    
    last_time = datetime.fromisoformat(last_logged)
    time_since = datetime.now() - last_time
    
    # If it's been more than 25 minutes since we last logged something,
    # and we're being called, probably worth checking
    return time_since > timedelta(minutes=25)

def append_summary_to_daily_note(summary: str) -> bool:
    """Append summary to daily note"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        vault_daily_note = Path(f"/data/kelly-vault/01-Daily/2026/{today}.md")
        
        if not vault_daily_note.exists():
            return False  # Don't create notes, just add to existing ones
        
        # Read current note
        content = vault_daily_note.read_text()
        
        # Prepare the entry
        timestamp = datetime.now().strftime('%H:%M')
        entry = f"- **{timestamp}**: {summary}"
        
        # Find or create Activity Log section
        if "## Activity Log" in content:
            # Add to existing Activity Log section
            section_start = content.find("## Activity Log")
            next_section = content.find("\n## ", section_start + 1)
            
            if next_section == -1:  # Activity Log section is last
                content = content.rstrip() + "\n" + entry + "\n"
            else:
                # Insert before next section
                before_next = content[:next_section]
                after_next = content[next_section:]
                content = before_next.rstrip() + "\n" + entry + "\n\n" + after_next
        else:
            # Create new Activity Log section at end
            content = content.rstrip() + "\n\n## Activity Log\n" + entry + "\n"
        
        # Write back to file
        vault_daily_note.write_text(content)
        return True
        
    except Exception as e:
        return False

def generate_session_summary():
    """Generate a simple summary of what we talked about recently"""
    
    # For now, return None - this would be where we'd analyze recent conversation
    # The key insight is we want this to be called FROM the heartbeat context
    # where we already have access to what just happened in the conversation
    
    return None

def main():
    """Main function - called from heartbeat to summarize recent activity"""
    import sys
    
    # Check if we should summarize
    if not had_recent_conversation():
        return 0
    
    # For now, manual summary - in real implementation this would analyze recent conversation
    if len(sys.argv) > 1:
        summary = ' '.join(sys.argv[1:])
        
        if append_summary_to_daily_note(summary):
            save_activity_timestamp()
            print(f"✅ Logged: {summary}")
        else:
            print("❌ Failed to log summary")
    else:
        print("Usage: python3 simple-session-summary.py \"summary text\"")
    
    return 0

if __name__ == "__main__":
    exit(main())
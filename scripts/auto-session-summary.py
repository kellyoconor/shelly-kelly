#!/usr/bin/env python3
"""
Auto Session Summary for Daily Notes

Automatically detects if meaningful conversation happened in the last 30 minutes
and logs a simple summary to the Activity Log section of Kelly's daily note.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

def get_last_summary_time():
    """Get when we last logged a summary"""
    state_file = "/data/workspace/memory/auto-summary-state.json"
    
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                data = json.load(f)
                return datetime.fromisoformat(data.get('last_summary_time', '2000-01-01T00:00:00'))
    except:
        pass
    
    return datetime(2000, 1, 1)  # Long time ago

def save_summary_time():
    """Record that we just logged a summary"""
    state_file = "/data/workspace/memory/auto-summary-state.json"
    
    try:
        data = {
            'last_summary_time': datetime.now().isoformat(),
            'last_summary_date': datetime.now().strftime('%Y-%m-%d')
        }
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, 'w') as f:
            json.dump(data, f)
    except:
        pass

def should_log_summary():
    """Check if enough time has passed to warrant a new summary"""
    last_summary = get_last_summary_time()
    time_since = datetime.now() - last_summary
    
    # Only log if it's been at least 20 minutes since last summary
    return time_since > timedelta(minutes=20)

def append_to_activity_log(summary: str) -> bool:
    """Append summary to Activity Log in vault daily note"""
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

def detect_conversation_context():
    """Try to detect what conversation might have happened recently"""
    
    # For now, we'll use simple heuristics based on when this is being called
    # In a full implementation, this would analyze recent conversation transcript
    
    # If we're being called, assume there might have been some interaction
    # The key is this will be called from heartbeat context where we know what happened
    
    current_hour = datetime.now().hour
    
    # Generate context-aware summaries based on timing and frequency
    if current_hour >= 22:  # Evening
        return "Late evening check-in and conversation"
    elif current_hour >= 18:  # Evening  
        return "Evening conversation and planning"
    elif current_hour >= 12:  # Afternoon
        return "Afternoon discussion and coordination"
    elif current_hour >= 6:   # Morning
        return "Morning check-in and planning"
    else:  # Late night
        return "Late night conversation"

def main():
    """Main function - called automatically from heartbeat"""
    import sys
    
    # Check if we should log a summary
    if not should_log_summary():
        # Too soon since last summary
        return 0
    
    # If a summary was provided as argument, use that
    if len(sys.argv) > 1:
        summary = ' '.join(sys.argv[1:])
    else:
        # For now, return without logging - we want manual control
        # In full implementation, this would analyze recent conversation
        return 0
    
    # Log the summary
    if append_to_activity_log(summary):
        save_summary_time()
        print(f"✅ Activity logged: {summary}")
        return 0
    else:
        print("❌ Failed to log activity")
        return 1

if __name__ == "__main__":
    exit(main())
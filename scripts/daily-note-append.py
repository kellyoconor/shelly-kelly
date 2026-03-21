#!/usr/bin/env python3
"""
Real-time daily note updater for Kelly's Obsidian vault.
Appends significant events/decisions to today's daily note as they happen.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

def append_to_daily_note(content, section="Notes"):
    """Append content to today's daily note in the specified section."""
    
    # Get today's date in ET (UTC-5 or UTC-4 depending on DST)
    # For simplicity, using UTC-5 (EST) - could be enhanced for DST
    et_offset = timezone(timedelta(hours=-5))
    today = datetime.now(et_offset)
    date_str = today.strftime("%Y-%m-%d")
    
    # Daily note path
    daily_note_path = f"/data/kelly-vault/01-Daily/2026/{date_str}.md"
    
    # Ensure the directory and file exist
    os.makedirs(os.path.dirname(daily_note_path), exist_ok=True)
    if not os.path.exists(daily_note_path):
        # Create basic template
        template = f"""# {today.strftime("%B %d, %Y")}

## Weather
- 

## Events
- 

## Health
- 

## Thoughts
- 

## Tasks
- 

## Notes
- 
"""
        with open(daily_note_path, 'w') as f:
            f.write(template)
    
    # Read current content
    with open(daily_note_path, 'r') as f:
        lines = f.readlines()
    
    # Find the section to append to
    section_found = False
    insert_index = len(lines)
    
    for i, line in enumerate(lines):
        if line.strip() == f"## {section}":
            section_found = True
            # Find next section or end of file
            for j in range(i + 1, len(lines)):
                if lines[j].startswith("## "):
                    insert_index = j
                    break
            else:
                insert_index = len(lines)
            break
    
    if not section_found:
        # Add the section
        lines.append(f"\n## {section}\n")
        insert_index = len(lines)
    
    # Format the content with timestamp
    timestamp = today.strftime("%I:%M %p")
    formatted_content = f"- **{timestamp}**: {content}\n"
    
    # Insert the content
    lines.insert(insert_index, formatted_content)
    
    # Write back to file
    with open(daily_note_path, 'w') as f:
        f.writelines(lines)
    
    print(f"Added to {section}: {content}")
    
    # Auto-push to ensure Kelly sees the changes in her vault
    try:
        import subprocess
        subprocess.run(["/data/workspace/scripts/auto-push-vault.sh"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Warning: Auto-push to vault failed, but content was saved locally")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 daily-note-append.py 'content to add' [section]")
        sys.exit(1)
    
    content = sys.argv[1]
    section = sys.argv[2] if len(sys.argv) > 2 else "Notes"
    
    append_to_daily_note(content, section)
#!/usr/bin/env python3
"""
Welly Vault Integration - Write insights to Kelly's daily notes
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

class WellyVaultWriter:
    def __init__(self):
        self.vault_path = Path("/data/kelly-vault")
        self.daily_path = self.vault_path / "01-Daily" / "2026"
        
    def append_to_daily_note(self, content: str, section: str = "Health") -> bool:
        """Append Welly insights to today's daily note"""
        today = datetime.now().strftime('%Y-%m-%d')
        note_path = self.daily_path / f"{today}.md"
        
        # Ensure directory exists
        note_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing content or create new
        if note_path.exists():
            existing_content = note_path.read_text()
        else:
            existing_content = f"# {today}\n\n"
        
        # Find or create the Health section
        lines = existing_content.split('\n')
        health_line_index = None
        next_section_index = None
        
        for i, line in enumerate(lines):
            if line.strip() == f"## {section}":
                health_line_index = i
            elif health_line_index is not None and line.startswith('## ') and not line.startswith(f"## {section}"):
                next_section_index = i
                break
        
        timestamp = datetime.now().strftime('%H:%M')
        welly_entry = f"- **{timestamp}**: {content} 💙"
        
        if health_line_index is not None:
            # Health section exists, add to it
            insert_index = next_section_index if next_section_index else len(lines)
            lines.insert(insert_index, welly_entry)
        else:
            # Create Health section
            lines.extend([f"## {section}", welly_entry, ""])
        
        # Write back
        note_path.write_text('\n'.join(lines))
        return True
    
    def log_welly_activity(self, interpreted_state: Dict, should_speak: bool, message: Optional[str] = None):
        """Log Welly's daily analysis to vault"""
        
        # Create summary
        recovery = interpreted_state.get('recovery_status', 'unknown')
        alignment = interpreted_state.get('mind_body_alignment', 'unknown') 
        push_risk = interpreted_state.get('push_risk', 'unknown')
        confidence = interpreted_state.get('confidence', 0)
        
        if should_speak and message:
            summary = f"Welly flagged: {message[:100]}..."
        elif confidence > 0.6:
            summary = f"Recovery {recovery}, alignment {alignment}, push risk {push_risk}"
        else:
            summary = f"Background monitoring (confidence {confidence:.1f})"
        
        self.append_to_daily_note(summary, "Health")

if __name__ == "__main__":
    # Test
    writer = WellyVaultWriter()
    writer.append_to_daily_note("Welly vault integration test", "Health")
    print("✅ Test entry added to daily note")
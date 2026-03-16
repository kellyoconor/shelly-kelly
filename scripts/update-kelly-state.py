#!/usr/bin/env python3
"""
Update Kelly State Working Memory File
Updates kelly-state.md with current state for workspace context loading
"""

import subprocess
import sys
from datetime import datetime

def update_kelly_state_file():
    """Generate and save Kelly State to kelly-state.md"""
    
    # Get Kelly State from our checker
    result = subprocess.run(['python3', '/data/workspace/scripts/kelly-state-check.py', 'compact'], 
                           capture_output=True, text=True)
    
    if result.returncode != 0:
        kelly_state = "Kelly State: Data sources unavailable right now."
    else:
        kelly_state = result.stdout.strip()
    
    # Create the kelly-state.md content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Kelly State - Working Memory

*Updated: {timestamp}*

{kelly_state}

---

**Usage Note:** This represents my current natural knowledge about Kelly. It quietly shapes my responses without being explicitly mentioned unless specifically relevant to the conversation.
"""

    # Write to kelly-state.md
    with open('/data/workspace/kelly-state.md', 'w') as f:
        f.write(content)
    
    print(f"Kelly State updated at {timestamp}")

if __name__ == "__main__":
    update_kelly_state_file()
#!/usr/bin/env python3
"""
Update Kelly State Working Memory File
Updates kelly-state.md with current state for workspace context loading
and writes a machine-readable active context snapshot.
"""

import json
import subprocess
import sys
from datetime import datetime

ACTIVE_CONTEXT_FILE = '/data/workspace/memory/active-kelly-context.json'
KELLY_STATE_FILE = '/data/workspace/kelly-state.md'


def parse_compact_state(kelly_state_text, timestamp):
    """Convert compact Kelly State text into a structured snapshot."""
    snapshot = {
        'updated_at': timestamp,
        'physical': '',
        'schedule': '',
        'focus': '',
        'tone': '',
        'open_loops': '',
        'avoid': '',
    }

    for line in (kelly_state_text or '').splitlines():
        if ': ' not in line:
            continue
        key, value = line.split(': ', 1)
        normalized = key.strip().lower()
        if normalized in snapshot:
            snapshot[normalized] = value.strip()
        elif normalized == 'open loops':
            snapshot['open_loops'] = value.strip()

    return snapshot


def update_kelly_state_file():
    """Generate and save Kelly State to kelly-state.md and JSON snapshot."""

    result = subprocess.run(
        ['python3', '/data/workspace/scripts/kelly-state-check.py', 'compact'],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        kelly_state = 'Kelly State: Data sources unavailable right now.'
    else:
        kelly_state = result.stdout.strip()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    content = f"""# Kelly State - Working Memory

*Updated: {timestamp}*

{kelly_state}

---

**Usage Note:** This represents my current natural knowledge about Kelly. It quietly shapes my responses without being explicitly mentioned unless specifically relevant to the conversation.
"""

    with open(KELLY_STATE_FILE, 'w') as f:
        f.write(content)

    snapshot = parse_compact_state(kelly_state, timestamp)
    with open(ACTIVE_CONTEXT_FILE, 'w') as f:
        json.dump(snapshot, f, indent=2)

    print(f"Kelly State updated at {timestamp}")


if __name__ == '__main__':
    update_kelly_state_file()

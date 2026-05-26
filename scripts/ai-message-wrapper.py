#!/usr/bin/env python3
"""
AI Message Wrapper with Kelly State Enforcement.
Uses the shared Kelly message pipeline so proactive sends fail closed.
"""

import json
import sys

from kelly_message_pipeline import prepare_message


def prepare_kelly_message(message_text=None, proactive=True):
    """Prepare for sending message to Kelly - use this before message tool."""
    print("🔄 Preparing Kelly-aware message...")
    return prepare_message(message_text=message_text, proactive=proactive)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        message_text = ' '.join(sys.argv[2:])
        result = prepare_kelly_message(message_text=message_text, proactive=True)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result['message_allowed'] else 1)
    prepare_kelly_message()

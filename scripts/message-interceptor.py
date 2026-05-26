#!/usr/bin/env python3
"""
Message Pipeline Interceptor
Intercepts messages to Kelly, enforces the shared quality gate for proactive sends,
and auto-updates Kelly State first.
"""

import subprocess
import sys
import time
from datetime import datetime

from message_quality_gate import validate_proactive_message

KELLY_NUMBER = "+[REDACTED_CLIENT_ID]401"
KELLY_STATE_UPDATE_SCRIPT = "/data/workspace/scripts/update-kelly-state.py"


def is_message_to_kelly(args):
    """Check if message is being sent to Kelly"""
    for i, arg in enumerate(args):
        if arg in ['--to', '--target']:
            if i + 1 < len(args) and args[i + 1] == KELLY_NUMBER:
                return True
    return False


def extract_message_arg(args):
    """Extract message text from openclaw message send args."""
    for i, arg in enumerate(args):
        if arg == '--message' and i + 1 < len(args):
            return args[i + 1]
    return None


def update_kelly_state():
    """Update Kelly State before messaging"""
    print(f"[{datetime.now()}] 🔄 Auto-updating Kelly State before message...")

    result = subprocess.run(['python3', KELLY_STATE_UPDATE_SCRIPT], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[{datetime.now()}] ⚠️  Kelly State update failed: {result.stderr}")
    else:
        print(f"[{datetime.now()}] ✅ Kelly State updated successfully")

    return result.returncode == 0


def validate_message_args(args):
    """Validate the outbound proactive message before send."""
    message_text = extract_message_arg(args)
    if message_text is None:
        return True, 'no-message-arg'
    return validate_proactive_message(message_text)


def main():
    """Intercept openclaw message calls and add Kelly State update + validation"""
    original_args = sys.argv[1:]

    if 'message' in original_args and 'send' in original_args and is_message_to_kelly(original_args):
        print(f"[{datetime.now()}] 📡 Detected message to Kelly - activating context update...")
        is_valid, reason = validate_message_args(original_args)
        if not is_valid:
            print(f"[{datetime.now()}] 🛑 Message blocked by quality gate ({reason})")
            return 1

        update_kelly_state()
        time.sleep(1)

    cmd = ['openclaw'] + original_args
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        ok, reason = validate_message_args(sys.argv[2:])
        print({'message_allowed': ok, 'reason': reason})
        raise SystemExit(0 if ok else 1)
    raise SystemExit(main())

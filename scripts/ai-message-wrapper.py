#!/usr/bin/env python3
"""
AI Message Wrapper with Kelly State Enforcement
Automatically ensures Kelly State is fresh before any message to Kelly
"""

import re
import subprocess
import sys
import os
from datetime import datetime

KELLY_NUMBER = "+[REDACTED_CLIENT_ID]401"
KELLY_STATE_FILE = "/data/workspace/kelly-state.md"
KELLY_STATE_ENFORCER = "/data/workspace/scripts/kelly-state-enforcer.py"


def is_kelly_targeted(channel=None, to=None, target=None, **kwargs):
    """Check if message targets Kelly"""
    targets = [to, target]
    return any(t == KELLY_NUMBER for t in targets if t)


def enforce_kelly_state_for_ai():
    """AI-specific Kelly State enforcement"""
    print("🤖 AI Message Pipeline: Enforcing Kelly State...")

    # Always update for AI-initiated messages (they're usually proactive)
    result = subprocess.run([
        sys.executable,
        "/data/workspace/scripts/update-kelly-state.py"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️ Kelly State update failed: {result.stderr}")
    else:
        print("✅ Kelly State updated for AI message")

    return result.returncode == 0


def load_kelly_state_context():
    """Ensure kelly-state.md is loaded as workspace context"""
    if os.path.exists(KELLY_STATE_FILE):
        with open(KELLY_STATE_FILE, 'r') as f:
            content = f.read()
        print("📖 Kelly State loaded as working memory context")
        return content
    else:
        print("⚠️ Kelly State file not found")
        return None


def build_quality_flags(message):
    """Estimate whether a proactive message has enough substance."""
    lowered = (message or '').lower()
    observation_markers = [
        'you ran', 'you slept', 'readiness', 'sleep', 'yesterday', 'today',
        'seems', 'looks like', 'i noticed', 'i’m noticing', "i'm noticing"
    ]
    interpretation_markers = [
        'which suggests', 'feels like', 'seems like', 'more like',
        'less like', 'might be', 'tells me', "doesn't mean", 'that means'
    ]
    action_markers = [
        'want me to', 'i can help', 'you could', 'might help', 'worth',
        'lean into', 'protect', 'keep it', 'today is a good day to', 'better than'
    ]

    flags = {
        'observation': any(marker in lowered for marker in observation_markers),
        'interpretation': any(marker in lowered for marker in interpretation_markers),
        'action': any(marker in lowered for marker in action_markers),
    }

    if not flags['observation'] and re.search(r'\b\d+(?:\.\d+)?\b', lowered):
        flags['observation'] = True

    return flags


def validate_proactive_message(message_text):
    """Reject literal, repetitive, or too-thin proactive messages."""
    if not message_text or not message_text.strip():
        return False, 'empty'

    lowered = message_text.lower()
    banned_patterns = [
        'usual starbucks',
        'did you get coffee',
        'how are you?',
        'how was your day',
        'have you run yet',
        'how did it feel? 🏃‍♀️',
        'how are you feeling energy-wise?',
        "how's your energy matching the data?",
    ]
    if any(pattern in lowered for pattern in banned_patterns):
        return False, 'literal-pattern'

    flags = build_quality_flags(message_text)
    if sum(1 for value in flags.values() if value) < 2:
        return False, f"low-signal:{flags}"

    return True, f"ok:{flags}"


# Expose functions for AI tool usage
def prepare_kelly_message(message_text=None, proactive=True):
    """Prepare for sending message to Kelly - use this before message tool."""
    print("🔄 Preparing Kelly-aware message...")
    enforce_kelly_state_for_ai()
    kelly_state = load_kelly_state_context()

    if proactive and message_text is not None:
        is_valid, reason = validate_proactive_message(message_text)
        if is_valid:
            print(f"✅ Proactive message passed quality gate ({reason})")
        else:
            print(f"🛑 Proactive message blocked by quality gate ({reason})")
        return {
            'kelly_state': kelly_state,
            'message_allowed': is_valid,
            'reason': reason,
        }

    return {
        'kelly_state': kelly_state,
        'message_allowed': True,
        'reason': 'no-message-validation',
    }


if __name__ == "__main__":
    # Command-line usage
    if len(sys.argv) > 1 and sys.argv[1] == 'validate':
        message_text = ' '.join(sys.argv[2:])
        result = prepare_kelly_message(message_text=message_text, proactive=True)
        print(result)
        sys.exit(0 if result['message_allowed'] else 1)
    prepare_kelly_message()

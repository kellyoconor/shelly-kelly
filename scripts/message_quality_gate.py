#!/usr/bin/env python3
"""
Shared proactive message quality gate.
Used by wrappers/senders so proactive messages fail closed when they are too literal or thin.
"""

import re
from typing import Dict, Tuple


def build_quality_flags(message: str) -> Dict[str, bool]:
    lowered = (message or '').lower()
    observation_markers = [
        'you ran', 'you slept', 'readiness', 'sleep', 'yesterday', 'today',
        'seems', 'looks like', 'i noticed', 'i’m noticing', "i'm noticing",
        'your body', 'pattern', 'recently'
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


def validate_proactive_message(message_text: str) -> Tuple[bool, str]:
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
        return False, f'low-signal:{flags}'

    return True, f'ok:{flags}'


if __name__ == '__main__':
    import sys
    text = ' '.join(sys.argv[1:])
    allowed, reason = validate_proactive_message(text)
    print({'message_allowed': allowed, 'reason': reason})
    raise SystemExit(0 if allowed else 1)

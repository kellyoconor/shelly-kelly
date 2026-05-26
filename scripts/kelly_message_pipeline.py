#!/usr/bin/env python3
"""
Shared Kelly outbound message pipeline.
Provides one choke point for Kelly-state refresh + proactive message validation
so every sender path can fail closed the same way.
"""

import json
import os
import subprocess
import sys
from typing import Callable, Dict, Optional, Tuple

from message_quality_gate import validate_proactive_message

KELLY_NUMBER = "+[REDACTED_CLIENT_ID]401"
KELLY_STATE_FILE = "/data/workspace/kelly-state.md"
KELLY_STATE_UPDATE_SCRIPT = "/data/workspace/scripts/update-kelly-state.py"

Logger = Callable[[str], None]


def is_kelly_target(target: Optional[str] = None, to: Optional[str] = None) -> bool:
    targets = [target, to]
    return any(value == KELLY_NUMBER for value in targets if value)


def refresh_kelly_state(logger: Logger = print) -> bool:
    logger("🔄 Updating Kelly State...")
    result = subprocess.run(
        [sys.executable, KELLY_STATE_UPDATE_SCRIPT],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        stderr = (result.stderr or '').strip()
        logger(f"⚠️ Kelly State update failed: {stderr}")
        return False

    logger("✅ Kelly State updated")
    return True


def load_kelly_state_context(logger: Logger = print) -> Optional[str]:
    if not os.path.exists(KELLY_STATE_FILE):
        logger("⚠️ Kelly State file not found")
        return None

    with open(KELLY_STATE_FILE, 'r') as f:
        content = f.read()

    logger("📖 Kelly State loaded as working memory context")
    return content


def prepare_message(
    message_text: Optional[str] = None,
    proactive: bool = True,
    refresh_state: bool = True,
    logger: Logger = print,
) -> Dict[str, object]:
    if refresh_state:
        refresh_kelly_state(logger=logger)

    kelly_state = load_kelly_state_context(logger=logger)

    if proactive and message_text is not None:
        allowed, reason = validate_proactive_message(message_text)
        if allowed:
            logger(f"✅ Proactive message passed quality gate ({reason})")
        else:
            logger(f"🛑 Proactive message blocked by quality gate ({reason})")
        return {
            'kelly_state': kelly_state,
            'message_allowed': allowed,
            'reason': reason,
        }

    return {
        'kelly_state': kelly_state,
        'message_allowed': True,
        'reason': 'no-message-validation',
    }


def validate_message(message_text: str) -> Tuple[bool, str]:
    return validate_proactive_message(message_text)


def _main() -> int:
    if len(sys.argv) < 2:
        print("Usage: kelly_message_pipeline.py <refresh|validate|prepare> [message]")
        return 1

    command = sys.argv[1]

    if command == 'refresh':
        return 0 if refresh_kelly_state() else 1

    if command == 'validate':
        message_text = ' '.join(sys.argv[2:])
        allowed, reason = validate_message(message_text)
        print(json.dumps({'message_allowed': allowed, 'reason': reason}, indent=2))
        return 0 if allowed else 1

    if command == 'prepare':
        message_text = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else None
        result = prepare_message(message_text=message_text, proactive=True)
        print(json.dumps(result, indent=2))
        return 0 if result['message_allowed'] else 1

    print(f"Unknown command: {command}")
    return 1


if __name__ == '__main__':
    raise SystemExit(_main())

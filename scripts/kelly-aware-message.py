#!/usr/bin/env python3
"""
Kelly-Aware Message Sender
Automatically updates Kelly State before sending proactive messages
and blocks weak/literal proactive sends.
"""

import subprocess
import sys
from message_quality_gate import validate_proactive_message


def send_kelly_aware_message(message, target="+[REDACTED_CLIENT_ID]401", channel="whatsapp", accountId="custom-1"):
    """Send message to Kelly with automatic state update and quality validation first"""

    is_valid, reason = validate_proactive_message(message)
    if not is_valid:
        print(f"🛑 Message blocked by quality gate ({reason})")
        return False

    print("🔄 Updating Kelly State before message...")

    update_result = subprocess.run([
        'python3', '/data/workspace/scripts/update-kelly-state.py'
    ], capture_output=True, text=True)

    if update_result.returncode != 0:
        print(f"⚠️ Kelly State update failed: {update_result.stderr}")
    else:
        print("✅ Kelly State updated")

    cmd = [
        'openclaw', 'message', 'send',
        '--channel', channel,
        '--to', target,
        '--account-id', accountId,
        '--message', message
    ]

    print(f"📤 Sending message to {target}...")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Message sent successfully")
        return True
    else:
        print(f"❌ Message failed: {result.stderr}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 kelly-aware-message.py <message> [target] [channel] [accountId]")
        return 1

    message = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "+[REDACTED_CLIENT_ID]401"
    channel = sys.argv[3] if len(sys.argv) > 3 else "whatsapp"
    accountId = sys.argv[4] if len(sys.argv) > 4 else "custom-1"

    success = send_kelly_aware_message(message, target, channel, accountId)
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

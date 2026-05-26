#!/usr/bin/env python3
"""
Kelly-Aware Message Sender.
Uses the shared Kelly outbound pipeline before sending proactive messages.
"""

import subprocess
import sys

from kelly_message_pipeline import prepare_message


def send_kelly_aware_message(message, target="+[REDACTED_CLIENT_ID]401", channel="whatsapp", accountId="custom-1"):
    """Send message to Kelly with shared state update + quality validation first."""

    result = prepare_message(message_text=message, proactive=True)
    if not result['message_allowed']:
        return False

    cmd = [
        'openclaw', 'message', 'send',
        '--channel', channel,
        '--to', target,
        '--account-id', accountId,
        '--message', message
    ]

    print(f"📤 Sending message to {target}...")

    send_result = subprocess.run(cmd, capture_output=True, text=True)

    if send_result.returncode == 0:
        print("✅ Message sent successfully")
        return True

    print(f"❌ Message failed: {send_result.stderr}")
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

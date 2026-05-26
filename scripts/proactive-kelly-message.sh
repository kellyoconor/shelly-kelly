#!/bin/sh

# Proactive Kelly Message Script
# Updates Kelly State before proactive messages and blocks literal/weak sends.

set -eu

if [ $# -lt 1 ]; then
    echo "Usage: $0 <message> [additional_message_args...]"
    exit 1
fi

MESSAGE="$1"
shift

echo "🔍 Validating proactive message..."
python3 /data/workspace/scripts/message_quality_gate.py "$MESSAGE"

echo "🔄 [$(date)] Updating Kelly State before proactive message..."
python3 /data/workspace/scripts/update-kelly-state.py

echo "📤 [$(date)] Sending proactive message to Kelly..."
openclaw message send \
    --channel whatsapp \
    --to "+13018302401" \
    --account-id custom-1 \
    --message "$MESSAGE" \
    "$@"

echo "✅ [$(date)] Message sent successfully"

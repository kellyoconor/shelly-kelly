#!/bin/sh

# Proactive Kelly Message Script
# Uses the shared Kelly message pipeline before sending proactive messages.

set -eu

if [ $# -lt 1 ]; then
    echo "Usage: $0 <message> [additional_message_args...]"
    exit 1
fi

MESSAGE="$1"
shift

echo "🔍 Preparing proactive Kelly message through shared pipeline..."
python3 /data/workspace/scripts/kelly_message_pipeline.py prepare "$MESSAGE" >/dev/null

echo "📤 [$(date)] Sending proactive message to Kelly..."
openclaw message send \
    --channel whatsapp \
    --to "+13018302401" \
    --account-id custom-1 \
    --message "$MESSAGE" \
    "$@"

echo "✅ [$(date)] Message sent successfully"

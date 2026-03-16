#!/bin/bash

# Proactive Kelly Message Script
# Automatically updates Kelly State before sending any proactive message to Kelly

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 <message> [additional_message_args...]"
    echo "Example: $0 'Good morning! How are you feeling?'"
    exit 1
fi

MESSAGE="$1"
shift  # Remove message from args, keep any additional args

echo "🔄 [$(date)] Updating Kelly State before proactive message..."

# Update Kelly State first
python3 /data/workspace/scripts/update-kelly-state.py

if [ $? -eq 0 ]; then
    echo "✅ [$(date)] Kelly State updated successfully"
else
    echo "⚠️  [$(date)] Kelly State update failed, continuing anyway..."
fi

echo "📤 [$(date)] Sending proactive message to Kelly..."

# Send message to Kelly using message tool
openclaw message send \
    --channel whatsapp \
    --to "+13018302401" \
    --account-id custom-1 \
    --message "$MESSAGE" \
    "$@"

if [ $? -eq 0 ]; then
    echo "✅ [$(date)] Message sent successfully"
else
    echo "❌ [$(date)] Message send failed"
    exit 1
fi
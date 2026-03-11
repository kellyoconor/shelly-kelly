#!/bin/bash
# Emergency session cleanup - run anytime to prevent balloons

echo "🧹 Emergency Session Cleanup"

echo "Current session sizes:"
find /data/.clawdbot -name "*.jsonl" -exec wc -l {} + | sort -nr | head -10

echo ""
echo "Deleting cron sessions >2 days old..."
find /data/.clawdbot/cron/runs/ -name "*.jsonl" -mtime +2 -delete

echo "Deleting main session transcripts >7 days old..."  
find /data/.clawdbot/agents/main/sessions/ -name "*.jsonl" -mtime +7 -delete

echo "✅ Cleanup complete!"

echo ""
echo "Current largest files:"
find /data/.clawdbot -name "*.jsonl" -exec wc -l {} + | sort -nr | head -5
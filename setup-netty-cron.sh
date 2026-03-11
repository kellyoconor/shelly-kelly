#!/bin/bash
# Setup script for Netty cron jobs

# Make netty.py executable
chmod +x /data/workspace/netty.py

# Add cron jobs to current crontab
echo "Setting up Netty cron jobs..."

# Create temporary cron file
CRON_FILE=$(mktemp)

# Get existing crontab (if any)
crontab -l > "$CRON_FILE" 2>/dev/null || echo "# Crontab" > "$CRON_FILE"

# Remove any existing Netty jobs
sed -i '/# Netty/d' "$CRON_FILE"
sed -i '/netty.py/d' "$CRON_FILE"

# Add Netty jobs
cat >> "$CRON_FILE" << 'EOF'

# Netty - Enhanced Gap Detector Subagent
# Full deep scan with intelligence layer every morning at 8:30 AM
30 8 * * * cd /data/workspace && python3 netty.py --subagent full >> /tmp/netty-cron.log 2>&1

# Light intelligent re-scan every 4 hours (12:30 PM, 4:30 PM, 8:30 PM)
30 12,16,20 * * * cd /data/workspace && python3 netty.py --subagent light >> /tmp/netty-cron.log 2>&1

EOF

# Install new crontab
crontab "$CRON_FILE"

# Clean up
rm "$CRON_FILE"

echo "✅ Netty cron jobs installed successfully!"
echo ""
echo "Schedule:"
echo "  - Full scan: 8:30 AM daily"
echo "  - Light scans: 12:30 PM, 4:30 PM, 8:30 PM daily"
echo ""
echo "Logs: /tmp/netty-cron.log"
echo "Output: /data/workspace/pending_checkins.md"
echo "Netty log: /data/kelly-vault/netty_log.md"
# Netty Cron Setup Instructions

Since this container doesn't have `crontab`, here are the cron entries to add manually:

## Cron Jobs to Add

Add these lines to your system crontab:

```bash
# Netty - Gap Detector System
# Full deep scan every morning at 8:30 AM
30 8 * * * cd /data/workspace && python3 netty.py full >> /tmp/netty-cron.log 2>&1

# Light re-scan every 4 hours (12:30 PM, 4:30 PM, 8:30 PM)  
30 12,16,20 * * * cd /data/workspace && python3 netty.py light >> /tmp/netty-cron.log 2>&1
```

## Manual Setup Commands

If you have crontab access:

```bash
# Edit crontab
crontab -e

# Add the above lines
# Save and exit

# Verify
crontab -l | grep netty
```

## Alternative: OpenClaw Scheduling

If using OpenClaw's internal scheduling system, create these scheduled tasks:

```javascript
// Full scan daily
{
  "name": "Netty Full Scan",
  "schedule": "30 8 * * *", 
  "command": "cd /data/workspace && python3 netty.py full",
  "enabled": true
}

// Light scans
{
  "name": "Netty Light Scan", 
  "schedule": "30 12,16,20 * * *",
  "command": "cd /data/workspace && python3 netty.py light", 
  "enabled": true
}
```

## Testing

Test Netty manually:

```bash
cd /data/workspace

# Full scan
python3 netty.py full

# Light scan  
python3 netty.py light

# Check output
cat pending_checkins.md
tail /data/kelly-vault/netty_log.md
```
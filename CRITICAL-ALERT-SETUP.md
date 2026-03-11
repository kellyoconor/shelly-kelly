# 🚨 Critical Alert Safeguard System - Setup & Integration Guide

## Quick Setup (5 Minutes)

### 1. Make Scripts Executable
```bash
chmod +x /data/workspace/critical-alert-engine.py
chmod +x /data/workspace/netty-urgent-adapter.py  
chmod +x /data/workspace/welly-health-monitor.py
chmod +x /data/workspace/alert-retry-processor.cjs
```

### 2. Test Basic Functionality
```bash
# Test critical alert creation
python3 /data/workspace/critical-alert-engine.py create "Test urgent message" URGENT manual test

# Test system status
python3 /data/workspace/critical-alert-engine.py status

# Test heartbeat integration
node /data/workspace/alert-retry-processor.cjs heartbeat
```

### 3. Verify Integration Files
Confirm these files were created/updated:
- ✅ `HEARTBEAT.md` (updated with critical alert checks)
- ✅ `critical-alerts.json` (tracking database) 
- ✅ `alert-delivery-log.md` (delivery logs)
- ✅ `escalated-alerts.md` (manual review queue)

## How It Works

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Netty Gaps      │    │ Welly Health    │    │ Manual Alerts   │
│ Detection       │    │ Monitoring      │    │ from Shelly     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼───────────────┐
                    │ Critical Alert Engine       │
                    │ (Urgency Classification)    │
                    └─────────────┬───────────────┘
                                  │
    ┌─────────────────────────────┼─────────────────────────────┐
    │                             │                             │
    ▼                             ▼                             ▼
┌───────────┐              ┌──────────────┐              ┌──────────────┐
│ CRITICAL  │              │   URGENT     │              │   NORMAL     │
│ Alerts    │              │   Alerts     │              │   Messages   │
└─────┬─────┘              └──────┬───────┘              └──────┬───────┘
      │                           │                             │
      │ 5,10,15min retries        │ 10,20min retries           │ Existing
      │ 30min email backup        │ 60min email backup         │ Proactive
      │ 2hr manual escalation     │ 3hr manual escalation      │ System
      │                           │                             │
      └───────────────────────────┼─────────────────────────────┘
                                  │
                      ┌───────────▼───────────┐
                      │ Heartbeat Integration │
                      │ (Every cycle check)   │
                      └───────────────────────┘
```

### Alert Flow Examples

**🚨 CRITICAL Alert Flow:**
1. Netty detects: "Flight tomorrow at 3:17 PM - boarding pass?"
2. Urgent adapter classifies as CRITICAL (flight < 24h)
3. Alert engine: Immediate WhatsApp with "🚨 CRITICAL" prefix
4. If no response: Retries at 5, 10, 15 minutes
5. If still no response: Email backup at 30 minutes
6. If still no response: Escalate for manual review at 2 hours

**⚠️ URGENT Alert Flow:**  
1. Welly detects: Sleep < 6 hours for 3 consecutive nights
2. Health monitor classifies as URGENT
3. Alert engine: WhatsApp with "⚠️ URGENT" prefix
4. If no response: Retries at 10, 20 minutes
5. If still no response: Email backup at 60 minutes
6. If still no response: Escalate for manual review at 3 hours

**📋 NORMAL Message Flow:**
1. Netty detects: "How are things going with mom?"
2. Urgent adapter classifies as NORMAL
3. Routes to existing proactive system
4. Standard 35-minute retry logic

## Usage for Shelly

### Creating Critical Alerts Manually

```bash
# Emergency health alert
python3 critical-alert-engine.py create "Kelly, I'm concerned about your chest pain mention - are you okay?" CRITICAL manual health

# Urgent travel reminder
python3 critical-alert-engine.py create "Flight check-in opens in 2 hours - have your confirmation?" URGENT manual travel

# Let system auto-classify
python3 critical-alert-engine.py create "Your heart rate has been elevated for 3 days" # Auto-detects as URGENT
```

### Checking System Health

```bash
# Quick status check
python3 critical-alert-engine.py status

# Full report
python3 critical-alert-engine.py report

# Check escalated items
cat escalated-alerts.md
```

### When Kelly Responds

```bash
# Auto-mark recent alerts when Kelly is active
python3 critical-alert-engine.py respond 30  # Mark last 30 minutes

# Mark specific alert
python3 critical-alert-engine.py respond alert_abc123

# Let heartbeat auto-detect activity (recommended)
node alert-retry-processor.cjs auto-mark
```

## Integration with Existing Systems

### Netty Gap Detection

The system automatically processes Netty outputs:

```bash
# Run manually to process pending gaps
python3 netty-urgent-adapter.py process

# Check what would be classified without routing
python3 netty-urgent-adapter.py analyze

# Test urgency classification
python3 netty-urgent-adapter.py test "Flight tomorrow at 2 PM!"
```

**Automatic Processing:** When Netty runs its cron jobs, urgent gaps are automatically promoted to the critical alert system.

### Welly Health Monitoring

Health alerts are automatically created:

```bash
# Run health assessment manually
python3 welly-health-monitor.py assess

# Check recent symptoms only
python3 welly-health-monitor.py symptoms

# Test with sample data
python3 welly-health-monitor.py test
```

**Automatic Processing:** Welly assessments run during heartbeats and create alerts for concerning patterns.

### Heartbeat Integration

The heartbeat now includes critical alert processing as the highest priority:

1. **Critical Alert Check** (every heartbeat) - Handles retries, escalations, auto-marking
2. **Welly Health Check** (every 3-4 heartbeats) - Monitors health patterns
3. **Enhanced Netty Check** (2-3x daily) - Processes gaps for urgency first
4. **Standard Checks** (existing) - Context monitoring, memory, email, etc.

### Proactive Message System

Normal priority messages continue using the existing proactive system. The critical alert system only handles URGENT and CRITICAL items.

## Monitoring & Maintenance

### Daily Checks (Automated)

The system generates daily reports automatically. Check these files:

- **`alert-delivery-log.md`** - All delivery attempts and results
- **`escalated-alerts.md`** - Items needing manual review  
- **`memory/welly-health-YYYYMMDD.md`** - Health assessment logs
- **`memory/netty-urgency-YYYYMMDD.md`** - Gap urgency processing logs

### Weekly Review

1. **Delivery Success Rate:** Are alerts reaching Kelly?
2. **False Positive Rate:** Are we flagging too many things as urgent?
3. **Response Times:** How quickly does Kelly respond to different urgency levels?
4. **Escalated Items:** Review manual escalation queue

### Tuning the System

**If too many false positives:**
- Edit urgency keywords in `critical-alert-engine.py`
- Adjust thresholds in `welly-health-monitor.py`
- Modify pattern matching in `netty-urgent-adapter.py`

**If missing important alerts:**
- Add keywords to critical/urgent patterns
- Lower health monitoring thresholds
- Add new gap detection patterns

**If delivery issues:**
- Check WhatsApp message tool functionality
- Configure email backup service
- Adjust retry timing intervals

## Email Backup Configuration

Currently, email backup is simulated. To enable real email delivery:

1. **Configure Email Service** (Gmail, SendGrid, etc.)
2. **Update `alert-retry-processor.cjs`:**
   ```javascript
   this.emailConfig = {
       enabled: true,
       service: 'gmail',
       user: 'kelly@example.com',
       apiKey: process.env.EMAIL_API_KEY
   };
   ```
3. **Implement email sending in `sendEmailBackup()` method**

## Troubleshooting

### Common Issues

**"Alert engine not found"**
- Check file paths are correct
- Ensure scripts are executable (`chmod +x`)

**"WhatsApp delivery failed"**  
- Test message tool: `openclaw tool message action=send channel=whatsapp message="test"`
- Check network connectivity
- Verify WhatsApp channel configuration

**"No gaps being processed"**
- Check if `pending_checkins.md` exists and has content
- Run Netty manually: `python3 netty.py full`
- Verify gap detection patterns

**"Health alerts not triggering"**
- Check memory files for symptom keywords
- Run health assessment manually: `python3 welly-health-monitor.py assess`
- Verify threshold settings

### Debug Commands

```bash
# Test full pipeline
python3 netty.py full                                    # Generate gaps
python3 netty-urgent-adapter.py process                  # Process urgency
python3 welly-health-monitor.py assess                   # Check health
node alert-retry-processor.cjs heartbeat                  # Run heartbeat check

# Check individual components
python3 critical-alert-engine.py status                  # Alert system status
cat critical-alerts.json                                 # Raw alert data
tail -f alert-delivery-log.md                           # Live delivery log
```

## Success Metrics

The system is working correctly when:

✅ **CRITICAL alerts** are delivered within 5 minutes and confirmed within 30 minutes  
✅ **URGENT alerts** are delivered within 10 minutes and confirmed within 60 minutes  
✅ **Email backup** triggers for failed WhatsApp deliveries  
✅ **Escalated items** are flagged for manual review within target timeframes  
✅ **False positive rate** is < 20% (Kelly agrees most urgent items were actually urgent)  
✅ **Kelly NEVER misses** critical health alerts or time-sensitive information  

---

*System Status: Active and monitoring Kelly's wellbeing 24/7* 🛡️
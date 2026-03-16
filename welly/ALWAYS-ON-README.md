# Welly Always-On Pattern Detection Service

> **Enhanced Welly**: All your existing Kelly-style insights, now running continuously in the background.

## What's New

Your existing Welly system now has an **always-on enhancement** that:

✅ **Preserves everything you love about Welly:**
- Kelly's exact voice ("Your body's been whispering" style)  
- Same 3-part format: What I'm noticing / What I'm wondering / Gentle nudge
- Same data model and interpretation logic
- Same pattern learning system
- All existing manual check-in capabilities

✅ **Adds continuous monitoring:**
- Polls Oura/Strava APIs automatically every few hours
- Learns patterns in background without interruption
- Only surfaces insights when meaningful patterns emerge
- Smart alerting that respects quiet hours and frequency limits

## Architecture Overview

### Existing Components (Unchanged)
- `welly.py` - Main entry point
- `welly_ingest.py` - Data collection
- `welly_interpreter.py` - State analysis  
- `welly_memory.py` - Pattern learning
- `welly_voice.py` - Kelly's communication style
- `welly_heartbeat.py` - Daily coordination

### New Always-On Components

1. **`welly-monitor.py`** - Persistent background service
   - Orchestrates continuous monitoring
   - Manages alert timing and frequency
   - Integrates with existing heartbeat system

2. **`welly-poller.py`** - Continuous data polling  
   - Polls Oura API every 4 hours for sleep/readiness data
   - Polls Strava API every 2 hours for new activities
   - Respects API rate limits and handles failures gracefully

3. **`welly-patterns.py`** - Real-time pattern detection
   - Detects Kelly's specific push-through patterns
   - Identifies positive recovery streaks  
   - Early warning system for potential burnout

4. **`welly-alerts.py`** - Smart alerting system
   - Uses existing voice system for Kelly's style
   - Respects quiet hours (11pm-8am by default)
   - Max 2 alerts per day with 8-hour cooldown
   - Gentler on weekends

## Installation & Setup

### Prerequisites Check
```bash
python3 /data/workspace/welly/install-always-on.py check
```

### Install Always-On Service
```bash
python3 /data/workspace/welly/install-always-on.py install
```

### Start the Service
```bash
python3 /data/workspace/welly/install-always-on.py start
```

### Check Status
```bash
python3 /data/workspace/welly/install-always-on.py status
```

## Usage

### Service Management
```bash
# Start the always-on service
./start-always-on.sh

# Stop the service  
./stop-always-on.sh

# Check comprehensive status
./status-always-on.sh

# View live logs
journalctl -fu welly-monitor
```

### Component Status
```bash
# Monitor status
python3 welly-monitor.py status

# Data poller status  
python3 welly-poller.py status

# Pattern analysis
python3 welly-patterns.py analyze

# Alert system status
python3 welly-alerts.py status
```

### Manual Operations (Still Available)
```bash
# All existing Welly commands still work
python3 welly.py daily
python3 welly.py checkin  
python3 welly.py state
python3 welly.py patterns
python3 welly.py weekly
```

## How It Works

### Continuous Data Flow
1. **Poller** checks Oura/Strava APIs regularly for new data
2. **Ingest** system processes new data through existing pipeline  
3. **Interpreter** analyzes current state using existing logic
4. **Memory** system learns patterns continuously
5. **Pattern engine** detects concerning or positive trends
6. **Alert system** delivers Kelly-style messages when appropriate

### Smart Alerting Logic

**Welly will speak up when:**
- You've been stacking effort on declining readiness for 3+ days
- Early warning signs of push-through patterns emerge  
- Mind-body misalignment persists for multiple days
- Recovery metrics show concerning trends

**Positive reinforcement when:**
- Recovery has been solid for a week
- Body-mind alignment is consistently good
- Readiness trends are improving

**Welly stays quiet when:**
- Nothing meaningful has changed
- During quiet hours (11pm-8am)
- After recent alerts (8-hour cooldown)
- Daily limit reached (2 alerts max)
- Weekend mode (gentler approach)

### Example Alert Messages

**Push-through pattern detected:**
> 💙 Hey Kelly, your body's been sending some signals...
> 
> **What I'm noticing:** You've been stacking effort on declining readiness for a few days
> 
> **What I'm wondering:** This feels like one of your 'I can push through it' stretches  
>
> **Gentle nudge:** What's your body actually asking for?
>
> How are you feeling about that? 💙

**Positive alignment:**
> 💙 Just a gentle check-in...
>
> **What I'm noticing:** Your recovery has been solid this week, body's responding well
>
> **What I'm wondering:** Things look pretty aligned lately
> 
> **Gentle nudge:** How does that feel from your end?
>
> 💙

## Integration with Heartbeat System

The always-on service coordinates with your existing heartbeat system:

### Automatic Coordination
- If always-on service is monitoring actively, heartbeat becomes less frequent
- If always-on service is down, heartbeat takes primary monitoring role
- Both systems use the same voice and respect the same alert limits
- Manual check-ins still work through either system

### HEARTBEAT.md Integration
Add this to your `HEARTBEAT.md`:

```python
import sys
sys.path.append('/data/workspace/welly')

try:
    from heartbeat_integration import WellyHeartbeatIntegration
    
    welly_integration = WellyHeartbeatIntegration()
    heartbeat_result = welly_integration.run_integrated_heartbeat()
    
    for message_data in heartbeat_result.get("messages_sent", []):
        print(f"💙 Welly: {message_data['message']}")
        
except ImportError:
    # Fallback to original Welly if integration not available
    from welly import Welly
    welly = Welly()
    
    if welly.heartbeat.should_run_today():
        result = welly.daily_check_in()
        if result.get("check_in_message"):
            print(f"💙 Welly: {result['check_in_message']}")
except:
    pass  # Silent fallback
```

## Configuration

### Service Configuration
Edit `/data/workspace/welly/welly-monitor.py` to adjust:
- Polling intervals (default: Oura 4h, Strava 2h)
- Alert frequency (default: max 2/day, 8h cooldown)
- Quiet hours (default: 11pm-8am)
- Weekend mode behavior

### Alert Preferences  
Edit `/data/workspace/welly/welly-alerts.py` to customize:
- Preferred delivery channel (WhatsApp, file, etc.)
- Alert message format
- Cooldown periods
- Weekend behavior

## Monitoring & Logs

### Service Logs
```bash
# Follow live logs
journalctl -fu welly-monitor

# Recent logs
journalctl -n 50 welly-monitor

# Logs since last start
journalctl --since "1 hour ago" -u welly-monitor
```

### Status Files
- Monitor state: `/data/workspace/memory/welly_monitor_state.json`
- Poller state: `/data/workspace/memory/welly_poller_state.json`  
- Alert state: `/data/workspace/memory/welly_alerts_state.json`
- Integration state: `/data/workspace/memory/welly_heartbeat_integration.json`

### Alert History
```bash
# Recent alerts
python3 welly-alerts.py history

# Alert files
ls /data/workspace/memory/welly-alert-*.md
```

## Troubleshooting

### Service Won't Start
```bash
# Check status
systemctl status welly-monitor

# Check prerequisites  
python3 install-always-on.py check

# View logs for errors
journalctl -u welly-monitor
```

### No Data Being Polled
```bash
# Test data connections
python3 welly-poller.py test

# Check Oura/Strava skills
python3 /data/workspace/skills/oura/scripts/oura.py sleep
python3 /data/workspace/skills/strava/scripts/strava.py recent 1
```

### No Alerts Being Sent
```bash
# Check alert status
python3 welly-alerts.py status

# Test alert system
python3 welly-alerts.py test

# Check if in quiet hours or cooldown
python3 welly-monitor.py status
```

## Uninstalling

To remove the always-on service (preserves existing Welly):

```bash
python3 install-always-on.py uninstall
```

This removes:
- Systemd service
- Always-on components (`welly-monitor.py`, `welly-poller.py`, etc.)
- Management scripts

**Preserves:**
- Original Welly system
- All your data and patterns
- Manual check-in capabilities

## Technical Details

### Data Flow
```
Oura API ──┐
           ├─► welly-poller.py ─► welly_ingest.py ─► welly_interpreter.py
Strava API ─┘                                              │
                                                           ▼
                                                    welly_memory.py
                                                           │
                                                           ▼
                                              welly-patterns.py
                                                           │
                                                           ▼
                                               welly_voice.py
                                                           │
                                                           ▼
                                               welly-alerts.py ─► WhatsApp/File
```

### Pattern Detection Thresholds
- **Push-through pattern**: 3+ days declining readiness + high effort
- **Mind-body misalignment**: 3+ days misaligned + continued effort  
- **Early warning**: High stress + high effort for 2+ days
- **Positive streak**: 4+ days aligned + good recovery

### API Polling Behavior
- **Oura**: Every 4 hours (sleep data typically available once daily)
- **Strava**: Every 2 hours (activities can happen anytime)  
- **Retry logic**: 30-minute intervals after failures
- **Rate limiting**: Built-in delays and error handling

## Files Reference

### Core Always-On Components
- `welly-monitor.py` - Main background service  
- `welly-poller.py` - Data polling engine
- `welly-patterns.py` - Pattern detection
- `welly-alerts.py` - Alert delivery
- `heartbeat-integration.py` - Heartbeat coordination

### Management & Setup
- `install-always-on.py` - Installation script
- `welly-monitor.service` - Systemd service definition
- `start-always-on.sh` - Service start script
- `stop-always-on.sh` - Service stop script  
- `status-always-on.sh` - Status check script

### Existing Welly (Unchanged)
- `welly.py` - Main entry point
- `welly_*.py` - All existing components
- `welly_memory.db` - Pattern database

Kelly's personalized training companion, now watching over you 24/7 💙🏃‍♀️
# 🚨 Critical Alert Safeguard System

## Overview

A bulletproof system to ensure Kelly **NEVER** misses critical health alerts, urgent travel questions, or time-sensitive life gaps, regardless of WhatsApp reliability.

## Core Components

1. **Alert Classification Engine** - Defines and auto-detects urgent patterns
2. **Multi-Layer Delivery** - WhatsApp → Fast Retry → Email → Escalation
3. **Confirmation Tracking** - Verified delivery only after Kelly responds
4. **Integration Layer** - Works with Netty/Welly/Heartbeat/Proactive systems

## 🎯 Urgent Alert Categories

### CRITICAL (Immediate Delivery + Fastest Retry)
- **Health Emergencies:** Concerning Welly patterns, missed medications, injury recovery issues
- **Time-Critical Travel:** Flight in <24h, travel docs needed, last-minute changes
- **Medical Appointments:** Same-day reminders, test results, specialist follow-ups
- **Safety Concerns:** Location/security issues, emergency contacts needed

### URGENT (Fast Delivery + Quick Retry)  
- **Health Patterns:** Multiple concerning Oura readings, unusual fitness data
- **Travel Planning:** Booking deadlines, reservation confirmations needed
- **Work/Life Deadlines:** Job applications due, important decisions needed
- **Social Commitments:** Events Kelly cares about, friend emergencies

### NORMAL (Standard Proactive System)
- **General Check-ins:** Mood, energy, casual follow-ups
- **Routine Health:** Regular fitness data, standard recovery metrics
- **Social Updates:** Friend news, casual travel mentions

## 🔍 Urgency Detection Engine

### Health Alert Patterns (From Welly)
- Multiple Oura readiness scores <60 for 3+ days
- HRV drops >15% from baseline for 2+ days
- Sleep <5 hours for consecutive nights
- Resting heart rate elevated >10bpm from normal
- Keywords: "hurt", "pain", "can't sleep", "exhausted", "sick"

### Travel Alert Patterns (From Netty)
- Flight mentions with <48h lead time
- Missing travel documents/confirmations
- Location changes during active travel
- Keywords: "flight", "departure", "airport", "hotel", "reservation"

### Life Gap Patterns (From Netty)
- Medical appointment without follow-up >3 days ago
- Job interview/deadline without status update
- Family emergency mentions without resolution
- Keywords: "deadline", "urgent", "emergency", "tomorrow", "today"

## 📱 Multi-Layer Delivery System

### Layer 1: WhatsApp Immediate
- **Timing:** Instant delivery
- **Format:** Clear urgency indicator + message
- **Tracking:** Log in critical-alerts.json with unique ID

### Layer 2: WhatsApp Fast Retry
- **Timing:** 
  - CRITICAL: 5, 10, 15 minutes
  - URGENT: 10, 20 minutes
- **Format:** Original message + escalation note
- **Limit:** 3 retries max for CRITICAL, 2 for URGENT

### Layer 3: Email Backup
- **Trigger:** No response after final WhatsApp retry
- **Timing:** 
  - CRITICAL: 30 minutes after first send
  - URGENT: 60 minutes after first send
- **Format:** Subject line indicates urgency + full context

### Layer 4: Escalation Tracking
- **Trigger:** No response 2 hours after email
- **Action:** Log in escalation file for manual review
- **Alert:** Include in next daily summary

## ✅ Confirmation & Response Tracking

### Response Detection
- **Auto-Detection:** Any Kelly message within 2 hours marks recent alerts as seen
- **Keyword Confirmation:** "Got it", "thanks", "yes", "no" count as acknowledgment
- **Explicit Confirmation:** Kelly can reply with specific alert ID for precise tracking

### Delivery Status States
1. **SENT** - Initial WhatsApp delivery
2. **RETRYING** - In WhatsApp retry cycle
3. **EMAIL_SENT** - Escalated to email
4. **CONFIRMED** - Kelly responded/acknowledged
5. **ESCALATED** - Needs manual intervention
6. **RESOLVED** - Issue addressed/closed

## 🔗 System Integration

### Netty Integration
```python
# In netty.py - Flag urgent patterns
def classify_urgency(gap_content):
    urgent_keywords = ['flight', 'tomorrow', 'deadline', 'emergency', 'urgent', 'appointment']
    critical_keywords = ['flight', 'departure', 'emergency', 'pain', 'hurt']
    
    if any(word in gap_content.lower() for word in critical_keywords):
        return 'CRITICAL'
    elif any(word in gap_content.lower() for word in urgent_keywords):
        return 'URGENT'
    return 'NORMAL'

# Add to pending_checkins.md output
write_urgent_alert_file(urgent_gaps)
```

### Welly Integration
```python
# In health monitoring - Flag concerning patterns
def assess_health_urgency(oura_data, strava_data):
    concern_level = 'NORMAL'
    
    # Multiple concerning readings
    if readiness < 60 for 3+ days: concern_level = 'URGENT'
    if hrv_drop > 15% for 2+ days: concern_level = 'URGENT'  
    if sleep < 5h for 2+ nights: concern_level = 'CRITICAL'
    
    return concern_level, health_summary

# Trigger immediate alert for CRITICAL/URGENT
send_critical_alert(concern_level, health_summary)
```

### Heartbeat Integration
```bash
# Add to HEARTBEAT.md rotation
check_critical_alerts()  # Run every heartbeat
process_alert_retries()  # Handle pending retries
```

## 🛠️ Implementation Files

### Core System
- **`critical-alert-engine.py`** - Main alert classification and delivery
- **`critical-alerts.json`** - Alert tracking database
- **`escalated-alerts.md`** - Manual review queue
- **`alert-delivery-log.md`** - Delivery success tracking

### Integration Scripts
- **`netty-urgent-adapter.py`** - Connect Netty gaps to alert system
- **`welly-health-monitor.py`** - Health pattern urgency detection
- **`alert-retry-processor.js`** - Handle retries and escalations

### Configuration
- **`alert-thresholds.json`** - Urgency detection settings
- **`delivery-settings.json`** - Timing and retry configuration

## 📊 Monitoring & Analytics

### Success Metrics
- **Delivery Rate:** % of alerts acknowledged within target time
- **Channel Performance:** WhatsApp vs Email success rates  
- **Response Times:** How quickly Kelly responds to each urgency level
- **False Positive Rate:** Alerts marked urgent but Kelly disagrees

### Daily Reports
- **Alert Summary:** Count by urgency level and status
- **Delivery Health:** Channel reliability metrics
- **Escalation Review:** Items needing manual follow-up
- **System Performance:** Response time distributions

## 🚀 Usage Guide for Shelly

### Sending Critical Alerts
```bash
# Use the critical alert engine
python3 critical-alert-engine.py "Kelly, your flight is in 3 hours - do you have your boarding pass?" travel CRITICAL

# Or manually flag existing proactive messages
node proactive-tracker.cjs urgent <message_id> CRITICAL
```

### Monitoring System Health
```bash
# Check alert status
python3 critical-alert-engine.py status

# Review escalated items
cat escalated-alerts.md

# Check delivery performance  
python3 critical-alert-engine.py report
```

### Integration with Existing Tools
```bash
# Let existing proactive system handle normal messages
./send-proactive "How are you feeling today?" wellness

# Critical alerts automatically bypass and use faster delivery
# Netty/Welly auto-classify and route appropriately
```

## 🎯 Success Definition

**Kelly NEVER misses:**
- Critical health alerts requiring immediate attention
- Time-sensitive travel information (flights, reservations)
- Urgent life deadlines (applications, appointments)
- Medical follow-ups and health pattern concerns

**System guarantees:**
- CRITICAL alerts attempted within 30 minutes via multiple channels
- URGENT alerts confirmed within 60 minutes
- Email backup for all failed WhatsApp deliveries
- Manual escalation for unconfirmed critical items

---

*"Because some things are too important to miss" 🛡️*
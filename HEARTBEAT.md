# HEARTBEAT.md

## 🚨 CRITICAL ALERT SYSTEM (EVERY HEARTBEAT - HIGHEST PRIORITY)
**Always check first - never skip:**
```bash
node /data/workspace/alert-retry-processor.cjs heartbeat
```
This handles:
- Processing urgent alert retries (5-15min intervals for CRITICAL, 10-20min for URGENT)
- Auto-marking alerts when Kelly is active
- Escalating to email backup if WhatsApp fails
- Checking for manual review items

**If output is NOT "HEARTBEAT_OK":** Report the alert status to Kelly immediately.
**If "HEARTBEAT_OK":** Continue to other checks below.

## 🩺 WELLY HEALTH MONITORING (Every 3-4 heartbeats)
**Run health pattern analysis:**
```bash
python3 /data/workspace/welly-health-monitor.py assess
```
- Monitors sleep, HRV, readiness patterns
- Scans memory for health symptom mentions
- Auto-creates CRITICAL/URGENT alerts for concerning patterns
- If assessment creates alerts: Those will be caught by critical alert system above

## 🏃‍♀️ WELLNESS CHECK (rotate every 2-3 heartbeats)
**Ask Welly (the health agent) to check:**
1. **Strava:** Latest run data — distance, pace, effort level
2. **Oura:** Recent sleep, readiness, HRV trends  
3. **Pattern analysis:** Cross-reference data (running through low readiness? Recovery patterns? Energy vs. numbers?)
4. **Proactive check-in:** Ask how things actually FELT, not just report numbers
5. If Welly finds significant activity/patterns: engage Kelly. If all quiet: continue to other checks.

## Context Monitoring (rotate every 2-3 heartbeats)  
Check main session token usage. If:
- **300k-320k tokens**: Gentle nudge to Kelly "Context getting full (X/400k) - might want to start a new session soon 🧹" 
- **320k-360k tokens**: More direct "Context almost full (X/400k) - recommend `/new` before continuing ⚠️"
- **Under 300k or over 380k**: Do nothing (under 300k is fine, over 380k Monty handles)

## Memory Size Check (rotate every 4-5 heartbeats)
Check MEMORY.md size: `python3 /data/workspace/scripts/memory-auto-trim.py` 
- If >3k chars: Auto-archives and reports to Kelly
- If trim occurred: Log to daily memory file

## 🔍 NETTY CHECK-INS (rotate 2-3x daily)
**Enhanced gap detection with urgency routing:**
1. **First, process gaps for urgency:** `python3 /data/workspace/netty-urgent-adapter.py process`
   - Auto-routes CRITICAL/URGENT gaps to alert system
   - Only NORMAL gaps remain in pending_checkins.md
2. **Then check normal gaps:** Read `/data/workspace/pending_checkins.md`
3. If normal gaps found: Pick most relevant prompt and ask Kelly naturally
4. If no normal gaps or prompts used: Move to manual check-ins below

**Note:** Critical travel/health gaps are now handled by alert system above, not heartbeat timing!

## Personal Check-ins (backup when Netty quiet)
- How are you feeling about NWSL after a few days to think?
- Atlanta guy still on your mind? Trip still happening?
- Any stress building up this week that you haven't mentioned?

## Other Checks (as time allows)
- Email (2-4 times per day)
- Calendar (upcoming 24-48h)

If nothing needs attention: HEARTBEAT_OK

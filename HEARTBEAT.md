# HEARTBEAT.md

📱 **Proactive Message Delivery:** For all proactive heartbeat messages:
1. Send to WhatsApp: accountId: custom-1, target: +13018302401
2. AND respond in UI chat with same message
Never use 'default' accountId or "Kelly" as target.

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

**Always continue to other checks below.** Only report if NEW urgent alerts are detected (not existing escalated ones).

## 🎯 PERSONAL CONTEXT CHECK (EVERY HEARTBEAT - HIGH PRIORITY)
**Check for significant events and personal engagement opportunities:**
```python
python3 /data/workspace/scripts/context-significance-check.py
```
**If personal check-in generated:**
- Send that message to Kelly and STOP (no system status needed)
- Personal connection always trumps system reports
- Example: "You had a massive engineering day building cognitive architecture. How are you feeling after all that intensive work?"

**If no significant events detected:**
- Continue to system checks below
- But still lead with caring: "Everything running smooth - how are YOU doing?"

## 💙 WELLY ALWAYS-ON CHECK (rotate every 2-3 heartbeats)
**Check if Always-On Welly is monitoring:**
```bash
cd /data/workspace/welly && ./status-always-on.sh | grep -q "✅ Running"
```
- If running: "💙 Always-On Welly is monitoring your patterns in background"
- If not running: Restart service and report to Kelly
- Check for any pattern alerts: `cat /data/workspace/memory/welly_heartbeat.json | tail -1`
- If Welly has insights ready: Share them

## 🔬 RESEARCH CO-PILOT STATUS (rotate every 2-3 heartbeats)
**Check research system activity:**
```bash
cd /data/workspace/kelly-research-copilot && python3 src/main.py --status
```
- **Monitor research activity**: New files created, topics discovered, research sessions
- **System health**: Check if monitoring is active, any errors
- **Report findings**: If research activity detected in last 24h, tell Kelly what was researched
- **Brief format**: "🔬 Research Co-Pilot active: 2 new research files on [topics]" or similar
- If no activity: continue to other checks

## 🚨 MANDATORY KELLY STATE PIPELINE (AUTOMATIC ENFORCEMENT)

**PIPELINE-LEVEL ENFORCEMENT:** Kelly State update is now **automatic** before any message to Kelly (+13018302401)

**📱 PROACTIVE MESSAGE DELIVERY:**
1. **Auto-update Kelly State:** `exec: python3 /data/workspace/scripts/update-kelly-state.py`
2. **Send to WhatsApp:** `message: accountId: custom-1, target: +13018302401` 
3. **AND respond in UI:** Same message content
Never use 'default' accountId or "Kelly" as target.

**FRESHNESS RULES:**
- **Proactive messages:** Always refresh Kelly State (no exceptions)
- **Kelly State expiry:** 20 minutes (auto-refresh if older)
- **Rapid replies:** 5-minute grace period for back-and-forth

**SYSTEM BEHAVIOR:**
- kelly-state.md automatically loaded as workspace context
- Pipeline prevents generic questions when context shows recent family drama, rest days, etc.
- AI composer cannot send message without fresh Kelly State

**ENFORCEMENT METHOD:**
```python
# Before any message tool to Kelly, run:
exec: python3 /data/workspace/scripts/ai-message-wrapper.py
```

**FAILURE MODE ELIMINATED:**
- System now prevents "How was your run this morning?" when context shows rest day + family issues
- Context awareness is automatic, not dependent on AI memory

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
4. **CRITICAL**: After sending a message, clear or mark it as sent in pending_checkins.md to avoid spam
5. If no normal gaps or prompts used: Move to manual check-ins below

**Note:** Critical travel/health gaps are now handled by alert system above, not heartbeat timing!

## Personal Follow-ups (when system checks are quiet)
**If no urgent alerts, no system issues, and no Netty gaps - focus on Kelly:**
- How is she feeling about recent decisions/projects?
- Any energy shifts or patterns to check on?
- Follow up on things she seemed uncertain about
- **Always lead with emotional/personal before data/status**
- **CRITICAL**: Check MEMORY.md "Resolved/Don't Ask About" section first

## Other Checks (as time allows)
- Email (2-4 times per day)
- Calendar (upcoming 24-48h)

If nothing needs attention: HEARTBEAT_OK
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

## 🧠 KELLY STATE UPDATE (every heartbeat - MANDATORY)
**BEFORE any proactive message, update Kelly State file:**
```bash
python3 /data/workspace/scripts/update-kelly-state.py
```
This updates `/data/workspace/kelly-state.md` with my current natural knowledge about Kelly.

**The file contains:**
- **Physical**: Recent running activity, health metrics (readiness/sleep)
- **Schedule**: Today's meetings and availability  
- **Focus**: Current projects, vault activity, research activity

**CRITICAL MENTAL SHIFT:** kelly-state.md is loaded as workspace context and represents things I naturally know about Kelly, NOT a report to analyze.

**Kelly State becomes working memory that:**
- Quietly shapes my responses and tone
- Prevents generic questions when context makes them awkward
- Informs what topics are relevant right now
- Stays in the background unless specifically relevant

**DO NOT constantly repeat Kelly State details back to her.**
**DO let Kelly State naturally influence how I respond.**

**Example:** If Kelly State shows "hasn't run since Thursday," don't ask "how was your run" and don't say "since you haven't run since Thursday." Just naturally avoid running questions and maybe be more gentle if she seems to be in a rest phase.

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

## Personal Check-ins (backup when Netty quiet)
**Read recent memory files first** to understand current context, then ask relevant follow-ups based on patterns from the past week:
- Follow up on topics/decisions you've been processing  
- Check in on stressors or situations you've mentioned
- Ask about things you seemed uncertain about
- **Base questions on YOUR actual patterns**, not generic prompts
- **CRITICAL**: Check MEMORY.md "Resolved/Don't Ask About" section first - never ask about topics listed there

## Other Checks (as time allows)
- Email (2-4 times per day)
- Calendar (upcoming 24-48h)

If nothing needs attention: HEARTBEAT_OK
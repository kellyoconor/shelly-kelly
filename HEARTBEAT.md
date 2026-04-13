# HEARTBEAT.md

**ROLE:** Urgent alerts & system monitoring only. **Morning briefing (6:30 AM) handles weather/health/personal check-ins.**

📱 **Proactive Message Delivery:** For all proactive heartbeat messages:
1. Send to WhatsApp: accountId: custom-1, target: +[REDACTED_CLIENT_ID]401
2. AND respond in UI chat with same message
Never use 'default' accountId or "Kelly" as target.

🔇 **Noise suppression:** If the WhatsApp gateway is connected for two heartbeat checks in a row, do **not** send another "gateway connected" update. Stay quiet unless there was a disconnect/reconnect transition, a new issue, or something meaningfully changed.

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

## 🎯 COMBINED CONTEXT CHECK (EVERY HEARTBEAT - HIGH PRIORITY)
**Check both external activities AND significant memory events:**
```python
python3 /data/workspace/scripts/combined-context-check.py
```
**This intelligently combines:**
- **External data**: Strava runs, Oura health, calendar events (full-context-check.py)
- **Memory analysis**: Emotional processing, work milestones, personal moments (context-significance-check.py)

**If personal check-in generated:**
- Send that message to Kelly and STOP (no system status needed)
- Personal connection always trumps system reports
- **Examples**: 
  - "Nice work on your run! ✅ Ran today: 7.03mi at 8:42/mi - how did it feel? 🏃‍♀️"
  - "You had a massive engineering day building cognitive architecture. How are you feeling after all that intensive work?"

**If no significant events detected:**
- Continue to system checks below
- **All hours**: Only reach out if urgent alerts or significant issues
- Default: HEARTBEAT_OK unless something needs attention
- **No special morning behavior** - heartbeat operates consistently all day

## 📝 SESSION SUMMARY (AUTOMATIC - EVERY HEARTBEAT)
**Always run after context checks - auto-log conversation:**
```python
python3 /data/workspace/scripts/check-and-log-conversation.py "SUMMARY_TEXT_HERE"
```
**What it does:**
- Checks if meaningful conversation happened in last 30 minutes
- If yes: writes simple 1-3 sentence summary to vault daily note
- Auto-creates "Activity Log" section with timestamp
- Only logs once per conversation (prevents spam)

**Examples it will capture:**
- **14:30**: Fixed duplicate heartbeat jobs, system working much better now
- **15:15**: Built recovery tracking for Welly, Kelly excited about logging stretching  
- **21:00**: Talked about feeling lonely, family not reaching out this week
- **22:25**: Kelly requested automatic session summary integration

**Key principle**: Just capture what actually happened, no categories or complexity needed

## 💙 WELLY FILTER CHECK (rotate every 2-3 heartbeats)
**Shelly checks Welly and filters for Kelly's attention:**
```python
python3 /data/workspace/welly/shelly_filter.py
```
**If kelly_should_know = true:** Send the kelly_message to Kelly immediately
**If kelly_should_know = false:** Just note background_info if present
**Auto-logs to vault:** Welly insights automatically append to daily note
**Filter criteria:** Only interrupt Kelly for mind-body misalignment, push patterns, emotional load, or concerning multi-day trends

## 📧 AGENTMAIL CHECK (rotate every 2-3 heartbeats)
**Check for important emails:**
```python
python3 /data/workspace/skills/agentmail/scripts/agentmail_cli.py threads --limit 5
```
- Check for unread emails in last 2-3 hours
- Flag urgent/important senders or subjects
- **Report format**: "📧 3 new emails - 1 from [important sender] about [subject]"
- If no new emails: continue to other checks

## 🔬 RESEARCH CO-PILOT STATUS (DISABLED - was over-triggering)
**CURRENTLY DISABLED** - Research system was triggering 15k+ sessions/day, way too aggressive
- System stopped per Kelly's request 
- Keep-alive disabled to prevent auto-restart
- Will need trigger logic tuning before re-enabling

## 🚨 MANDATORY KELLY STATE PIPELINE (AUTOMATIC ENFORCEMENT)

**PIPELINE-LEVEL ENFORCEMENT:** Kelly State update is now **automatic** before any message to Kelly (+[REDACTED_CLIENT_ID]401)

**📱 PROACTIVE MESSAGE DELIVERY:**
1. **Auto-update Kelly State:** `exec: python3 /data/workspace/scripts/update-kelly-state.py`
2. **Send to WhatsApp:** `message: accountId: custom-1, target: +[REDACTED_CLIENT_ID]401` 
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

## 🌅 SIMPLIFIED MORNING APPROACH
**No more morning quiet hours - heartbeat operates normally all day:**
- If context check generates a personal message → send it (any time of day)
- If no significant events → HEARTBEAT_OK (any time of day)
- Scheduled briefing can run alongside heartbeat without conflicts
- **Never leave Kelly without check-ins due to scheduling assumptions**

## Personal Follow-ups (when system checks are quiet)
**Only when something specific needs attention:**
- Important decisions she seemed conflicted about
- Follow-up on things she asked to be reminded about
- **CRITICAL**: Check MEMORY.md "Resolved/Don't Ask About" section first
- **Default**: HEARTBEAT_OK unless there's a specific reason to check in
- **Scheduled briefing handles structured morning check-ins (when it works!)**

## Version Management (rotate every 2 weeks)
**Check for OpenClaw updates:**
```bash
cd /openclaw && git fetch --tags && git tag -l 'v2026*' | tail -5
```
- Look for incremental updates (2026.2.10, 2026.2.11, etc.)
- Suggest updates for small version bumps only
- Flag major jumps (2026.2.x to 2026.3.x) for planned upgrade sessions
- **Goal**: Stay current, avoid big scary migrations

## Other Checks (rotate, low priority)
- Calendar (only if urgent events <2h away)
- Version updates (only flag critical security updates)

**DEFAULT**: HEARTBEAT_OK (stay quiet, let morning briefing handle regular check-ins)
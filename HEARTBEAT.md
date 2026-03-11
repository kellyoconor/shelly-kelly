# HEARTBEAT.md

## Context Monitoring (rotate every 2-3 heartbeats)
Check main session token usage. If:
- **300k-320k tokens**: Gentle nudge to Kelly "Context getting full (X/400k) - might want to start a new session soon 🧹" 
- **320k-360k tokens**: More direct "Context almost full (X/400k) - recommend `/new` before continuing ⚠️"
- **Under 300k or over 380k**: Do nothing (under 300k is fine, over 380k Monty handles)

## Memory Size Check (rotate every 4-5 heartbeats)
Check MEMORY.md size: `python3 /data/workspace/scripts/memory-auto-trim.py` 
- If >3k chars: Auto-archives and reports to Kelly
- If trim occurred: Log to daily memory file

## Personal Check-ins (rotate daily)
- How are you feeling about NWSL after a few days to think?
- Atlanta guy still on your mind? Trip still happening?
- Any stress building up this week that you haven't mentioned?
- Running feeling good or are you pushing through something?

## Other Checks
- Email (2-4 times per day)
- Calendar (upcoming 24-48h)

If nothing needs attention: HEARTBEAT_OK

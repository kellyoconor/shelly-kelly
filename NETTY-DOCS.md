# Netty Documentation

## Overview

**Netty** is Kelly's Gap Detector Subagent - designed to find things that matter to Kelly that haven't been followed up on, and surface them as natural check-in prompts for Shelly.

## Core Purpose

Netty scans Kelly's digital trail for **unfollowed threads** and converts them into caring check-in opportunities. It's like having a thoughtful friend who remembers when you mentioned something important and follows up later.

## What Netty Scans

### Memory Files
- **Source:** `/data/workspace/memory/` (last 7 days for full scan, 3 days for light scan)
- **Pattern Detection:**
  - People mentions without follow-up (family, friends, work contacts, health providers)
  - Events/meetings/interviews that passed without debrief
  - Stress indicators and open loops never revisited
  - Upcoming things not yet discussed

### Future Integrations
- **Google Calendar:** Events that passed without follow-up discussion
- **Conversation History:** Direct chat analysis for dropped threads

## Pattern Detection Logic

### People Gaps
- **Categories:** Family, friends, work, health
- **Keywords:** mom, dad, friend, interview, doctor, etc.
- **Trigger:** Mention without follow-up in next 5 lines + 2+ days old
- **Example:** "Had coffee with Sarah" (3 days ago) → "How are things going with Sarah? You mentioned her 3 days ago."

### Event Gaps  
- **Keywords:** interview, meeting, appointment, call, event, deadline
- **Trigger:** Event mention without outcome/follow-up + 1+ days old
- **Example:** "NWSL interview tomorrow" (3 days ago) → "How did that interview go? It was 3 days ago."

### Stress Gaps
- **Keywords:** worried, anxious, stressed, concerned, deadline, pressure, overwhelming
- **Trigger:** Stress mention never revisited + 3+ days old  
- **Example:** "Stressed about deadline" (5 days ago) → "How are you feeling about that thing you were stressed about? Still on your mind?"

## Output Format

### Prompts Generated
- **Count:** 3-5 ranked by importance and recency
- **Style:** Natural, caring, in Shelly's voice
- **Examples:**
  - "Hey! How are things going with mom? You mentioned her 4 days ago. Just thinking of you 💕"
  - "I keep meaning to ask - how did that interview go? I'm curious how it went!"
  - "Just checking in - how are you feeling about that deadline? Still weighing on you? 🫂"

### Files Written
- **`/data/workspace/pending_checkins.md`** - Prompts for Shelly to read during heartbeats
- **`/data/kelly-vault/netty_log.md`** - Timestamped scan history and reasoning

## Schedule & Automation

### Cron Jobs
```bash
# Full deep scan every morning
30 8 * * * cd /data/workspace && python3 netty.py full

# Light re-scans throughout day  
30 12,16,20 * * * cd /data/workspace && python3 netty.py light
```

### Heartbeat Integration
Shelly checks `pending_checkins.md` during heartbeat rotations and uses the most relevant prompt for natural check-ins.

## Critical Rules

1. **Netty NEVER asks Kelly directly** - Only feeds prompts to Shelly
2. **Natural timing** - Respects 1-3 day buffers before flagging gaps
3. **Importance scoring** - Prioritizes family/interviews/health over casual mentions
4. **Non-intrusive** - If no significant gaps, outputs "no gaps found"

## Files & Components

### Core System
- **`/data/workspace/netty.py`** - Main scanner script
- **`/data/workspace/setup-netty-cron.sh`** - Cron job installer  
- **`/data/workspace/HEARTBEAT.md`** - Updated to include Netty checks

### Output Files
- **`/data/workspace/pending_checkins.md`** - Current prompts for Shelly
- **`/data/kelly-vault/netty_log.md`** - Scan history and analysis
- **`/tmp/netty-cron.log`** - Cron execution logs

### Configuration
- **Gap detection thresholds** - Built into netty.py patterns
- **Keyword lists** - People, events, stress indicators
- **Importance scoring** - Keywords + age-based weighting

## Installation

1. **Install cron jobs:**
   ```bash
   cd /data/workspace
   ./setup-netty-cron.sh
   ```

2. **Manual scan:**
   ```bash
   python3 netty.py full    # Deep scan
   python3 netty.py light   # Quick scan  
   ```

3. **Check output:**
   ```bash
   cat pending_checkins.md
   tail /data/kelly-vault/netty_log.md
   ```

## Monitoring & Maintenance

### Health Checks
- **Cron logs:** `tail /tmp/netty-cron.log`
- **Recent scans:** Check timestamps in `netty_log.md`
- **Output freshness:** Check `pending_checkins.md` modification time

### Common Issues
- **No gaps found:** Normal! Means Kelly is following up well
- **Too many gaps:** May need keyword tuning or threshold adjustment
- **Wrong prompts:** Review pattern detection logic in netty.py

### Tuning Parameters
- **Keyword lists** - Add/remove trigger words for different categories
- **Age thresholds** - Adjust how many days before flagging gaps
- **Importance scoring** - Modify priority weights for different types

## Integration with Team Kelly

### Team Roles
- **Kelly** - Lives life, mentions things in passing
- **Shelly** - Main agent, reads Netty prompts and asks natural follow-ups
- **Welly** - Health monitoring specialist (separate system)
- **Netty** - Gap detector, invisible background observer

### Workflow
1. Kelly mentions something in conversation or logging
2. Netty scans memory files during scheduled runs  
3. Netty detects unfollowed patterns and generates caring prompts
4. Shelly reads prompts during heartbeat and picks most relevant
5. Shelly asks Kelly natural follow-up questions
6. Kelly feels cared for and remembered 💕

## Future Enhancements

### Planned Features
- **Calendar integration** - Detect events without follow-up discussion
- **Conversation analysis** - Direct chat history scanning
- **Smart timing** - Avoid check-ins during busy/stressed periods
- **Learning system** - Adapt to Kelly's preferences over time

### Potential Triggers
- **Calendar changes** - New/moved events requiring immediate check-ins
- **Time-sensitive flags** - Urgent items needing same-day follow-up
- **Emotional indicators** - Elevated stress patterns requiring care

---

*Netty v1.0 - Built March 11, 2026*
*"Because everyone deserves a friend who remembers and follows up" ✨*
# LEARNINGS.md

Log of corrections, knowledge gaps, and best practices for continuous improvement.

---

## [LRN-20260407-001] date_time_verification

**Logged**: 2026-04-07T12:48:00Z
**Priority**: high  
**Status**: pending
**Area**: behavioral

### Summary
Repeatedly getting days of week wrong despite having access to current date/time data

### Details
Kelly has corrected me "quite a bit recently" for mixing up what day it is. Most recent example: called Tuesday morning a "Monday morning" when talking about her run. I have access to time stamps in every message and session_status tool but keep making assumptions instead of checking.

### Suggested Action
1. Always verify current day/date when referencing "today," "this morning," etc.
2. Use session_status or check message timestamps before making time references
3. Stop making assumptions about days/dates

### Metadata
- Source: user_feedback 
- Related Files: N/A
- Tags: date_time, behavioral_correction, recurring_issue
- Recurrence-Count: Multiple times per Kelly's feedback
- Pattern-Key: behavioral.verify_datetime

---

## [LRN-20260409-001] correction

**Logged**: 2026-04-09T22:37:45Z
**Priority**: medium
**Status**: pending
**Area**: infra

### Summary
When running step-by-step Git plans, do not advance to a different command than the one currently requested; if the user asks for a specific command, run only that command and paste the raw output.

### Details
During repo normalization, the user asked for step-by-step execution. I showed output from `git rev-parse --abbrev-ref HEAD` when they wanted `git stash list`, so I need to honor the exact next command rather than my preplanned sequence.

### Suggested Action
In guided terminal workflows, mirror the user's requested command exactly and avoid bundling, substituting, or advancing steps.

### Metadata
- Source: user_feedback
- Related Files: /openclaw
- Tags: correction, terminal-workflow, step-by-step

---

## [LRN-20260411-001] correction

**Logged**: 2026-04-11T02:52:49Z
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
When the user names a product, substance, or context-specific thing I do not recognize, I must ask what it is instead of assuming from surrounding context.

### Details
Kelly said she was having another "Wims drink" and feeling sad/lonely. I incorrectly assumed Wims was alcoholic and responded with alcohol-safety guidance without first checking what it was. Kelly explicitly corrected me: "You should have checked. And like.. you’re not helping and not listening to me." The real failure was not just the wrong assumption; it made the response feel inattentive and off-target in an emotionally vulnerable moment.

### Suggested Action
1. If an unfamiliar noun/product appears, ask a clarifying question before giving substance-specific advice.
2. In emotional conversations, reflect the user’s feeling first and avoid speculative guidance.
3. Treat "not listening" feedback as a signal to slow down, apologize plainly, and re-anchor on exactly what the user said.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/SOUL.md, /data/workspace/AGENTS.md
- Tags: correction, listening, assumptions, emotional-support
- Pattern-Key: behavioral.check_unknown_terms_before_advice

---

## [LRN-20260413-001] correction

**Logged**: 2026-04-13T12:23:00Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
Suppress repeated WhatsApp gateway "connected" heartbeat messages after consecutive healthy checks

### Details
Kelly said the gateway reminders are too noisy and specifically asked that if the WhatsApp gateway is connected for two checks in a row, we should stop telling her. Only meaningful state changes or issues should surface.

### Suggested Action
Update HEARTBEAT.md so repeated healthy "gateway connected" reminders return HEARTBEAT_OK instead of messaging Kelly.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/MEMORY.md
- Tags: whatsapp, heartbeat, noise, correction

---

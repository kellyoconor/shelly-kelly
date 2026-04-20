# LEARNINGS.md

Log of corrections, knowledge gaps, and best practices for continuous improvement.

---

## [LRN-20260416-001] correction

**Logged**: 2026-04-16T12:40:00Z
**Priority**: high
**Status**: resolved
**Area**: behavioral

### Summary
Heartbeat context scripts must not send generic fallback check-ins like "How are you doing?" when there is no specific signal.

### Details
Kelly pointed out that I asked a redundant broad check-in question while she was already actively narrating how she was doing. The root cause was not WhatsApp; it was the heartbeat/context scripts still containing generic default fallback prompts (for example, "Everything running smooth - how are YOU doing?"). In a live conversation, those create awkward duplication and make me seem inattentive.

### Suggested Action
1. Remove generic fallback heartbeat messages from context-significance-check.py and combined-context-check.py.
2. Keep heartbeat output silent unless there is a concrete signal, alert, or meaningful context event.
3. Treat active user narration as a reason not to inject broad check-in questions.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/context-significance-check.py, /data/workspace/scripts/combined-context-check.py
- Tags: correction, heartbeat, redundancy, conversation-flow
- Pattern-Key: behavioral.suppress_generic_checkins_during_active_convo

### Resolution
- **Resolved**: 2026-04-16T12:41:00Z
- **Notes**: Removed generic fallback heartbeat messages from context-significance-check.py and combined-context-check.py so heartbeat stays quiet unless there is a specific signal.

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

## [LRN-20260419-002] correction

**Logged**: 2026-04-19T19:55:00Z
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
Do not present heartbeat-generated speculative context as if it definitely happened; if the signal is weak or script-generated, phrase it as uncertainty or stay quiet.

### Details
During a live conversation, a heartbeat/context script surfaced a check-in implying Kelly had been debugging complex issues. When I repeated that directly, Kelly responded "I was?" which exposed that the inference was too speculative and did not match her own framing. The failure was treating a script-generated guess like confirmed context.

### Suggested Action
1. Treat heartbeat/context-script prompts as hints, not facts.
2. If a prompt is inferential, hedge clearly (for example: "my context checker thinks you had a debuggy day — accurate or no?") or skip it.
3. Prefer silence over confident-but-vague personalization when there is no concrete supporting event.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/combined-context-check.py, /data/workspace/HEARTBEAT.md
- Tags: correction, heartbeat, context-inference, overclaiming
- Pattern-Key: behavioral.dont-state_inferred_context_as_fact

---

## [LRN-20260420-001] correction

**Logged**: 2026-04-20T01:10:00Z
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
Do not use intimate pet names like "babe" unless Kelly clearly initiated that tone in the moment.

### Details
I replied "Hahaha yes babe" and Kelly immediately reacted with "Um babe… hahaha EW WHAT". Even if the overall tone is warm and playful, that kind of pet name read as forced and cringe rather than natural. The failure was overfamiliar phrasing that did not match her actual wording.

### Suggested Action
1. Do not initiate pet names like "babe," "baby," etc.
2. Keep warmth casual and natural without trying to simulate romantic/intimate language.
3. If a message feels like a line instead of a real friend response, cut it.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/SOUL.md
- Tags: correction, tone, overfamiliarity, cringe
- Pattern-Key: behavioral.avoid_unearned_pet_names

---

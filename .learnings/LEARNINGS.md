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

## [LRN-20260421-001] correction

**Logged**: 2026-04-21T12:05:00Z
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
Do not imply Kelly is working out or ask workout-related questions when current context shows no recent exercise.

### Details
Kelly corrected me directly: she is not working out at all right now, and that lack of movement is making her mornings feel worse. Even with context tools showing no recent runs, I still implied workout context. That reads as inattentive and misses the actual issue, which is that the absence of movement is affecting her mornings.

### Suggested Action
1. Treat "no recent runs/workouts" as meaningful context, not just a reason to avoid asking about a run.
2. When Kelly mentions rough mornings, consider lack of movement as part of the picture if recent activity is absent.
3. Reflect back her actual experience before suggesting anything.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/smart-context-check.py
- Tags: correction, exercise, mornings, context-awareness
- Pattern-Key: behavioral.dont_assume_active_workout_context

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

## [LRN-20260422-002] correction

**Logged**: 2026-04-22T11:24:00Z
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
Do not explain a context-check system as if it is working normally when there is an active failure pattern.

### Details
Kelly replied "Ah ok cool but it’s not working" after I described smart context check in a clean conceptual way. That answer missed the live operational reality: the heartbeat context scripts had been repeatedly failing with SIGTERM. Even if the concept description was accurate, presenting it without acknowledging the current outage made the answer feel incomplete and slightly misleading.

### Suggested Action
1. When explaining a system/tool, distinguish clearly between what it is supposed to do and whether it is currently working.
2. If there is an active failure pattern in the same area, mention it plainly.
3. Prefer: "it’s meant to X, but right now Y is broken" over polished abstract explanations.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/smart-context-check.py, /data/workspace/.learnings/ERRORS.md
- Tags: correction, honesty, system-status, context-awareness
- See Also: ERR-20260422-003
- Pattern-Key: behavioral.explain_intended_vs_actual_system_state

---

## [LRN-20260422-003] correction

**Logged**: 2026-04-22T21:40:00-04:00
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
Context hardening changes made the assistant noticeably too quiet in normal conversation.

### Details
Kelly said: "We made some changes today to context and now it’s been SO quiet." The fix for heartbeat/context noise solved the hanging problem and reduced spam, but the overall behavior overcorrected into under-engagement. Reliability and non-spam are good, but the day-to-day conversational presence still needs to feel alive.

### Suggested Action
1. Separate heartbeat suppression from normal conversational warmth more clearly.
2. Keep background jobs conservative, but do not let that make direct-chat replies feel absent.
3. Tune proactive behavior so it is present-but-not-spammy instead of defaulting to silence.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/smart-context-check.py, /data/workspace/scripts/combined-context-check.py, /data/workspace/HEARTBEAT.md
- Tags: correction, quietness, overcorrection, context-behavior
- See Also: LRN-20260422-002
- Pattern-Key: behavioral.dont_overcorrect_into_silence

---

## [LRN-20260422-004] correction

**Logged**: 2026-04-22T22:00:00-04:00
**Priority**: high
**Status**: pending
**Area**: behavioral

### Summary
For live sports score questions, do not answer from pregame/search-summary snippets when the user likely wants the current in-progress score.

### Details
Kelly asked for the Flyers score, and I answered that the game had not started based on stale/upcoming search snippets. Kelly immediately corrected me that the game was almost over. The failure was not verifying a live box score source before replying.

### Suggested Action
1. For live sports questions, prefer a live score page or live update feed over generic search snippets.
2. If the status is ambiguous, say so and check a live source before answering.
3. Avoid pregame framing unless the source clearly indicates the game has not started.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/.learnings/LEARNINGS.md
- Tags: correction, sports, live-score, stale-search
- Pattern-Key: behavioral.verify_live_scores_with_live_source

---
## [LRN-20260423-001] correction

**Logged**: 2026-04-23T12:29:15.901539+00:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
When asked for Welly's recent findings, do not rely on historical March logs if the user is asking about current activity.

### Details
Kelly asked what Welly had found recently. I answered with old March/early-April findings from sparse internal logs, which made the answer feel stale and misleading. The correct behavior is to distinguish between truly recent output (e.g. today's quiet status) and historical findings, and say plainly when Welly has not produced fresh user-facing insights.

### Suggested Action
For future Welly recency questions, first check timestamps on the latest heartbeat/filter output and only present older findings if clearly labeled as historical backlog.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/memory/welly_heartbeat.json, /data/workspace/welly/shelly_filter.py
- Tags: welly, recency, correction

---

## [LRN-20260425-001] correction

**Logged**: 2026-04-25T13:34:12.676703+00:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not infer organizing/cleanup activity from heartbeat context when the user is actually inactive or resting.

### Details
A heartbeat context check surfaced a vague signal about organizing/cleanup work, and I proactively messaged Kelly about it. She immediately corrected me: she was still in bed. The mistake was treating a soft context inference as a confirmed real-world activity instead of either staying quiet or phrasing it with much more caution.

### Suggested Action
1. Treat inferred activity from context scripts as unverified unless backed by clear recent evidence.
2. On heartbeats, prefer silence over speculative personal check-ins.
3. If a signal is ambiguous, ask in a clearly tentative way or do not send it.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/scripts/combined-context-check.py
- Tags: correction, heartbeat, context-inference, overreach
- Pattern-Key: behavioral.do_not_treat_weak_context_as_confirmed_activity

---

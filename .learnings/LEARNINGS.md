## [LRN-20260514-001] correction

**Logged**: 2026-05-14T12:18:11Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
When Kelly is pointing at a message in chat, focus on the actual message content and conversational intent before explaining metadata wrappers.

### Details
In a WhatsApp conversation, Kelly said "See exactly" and then clarified "No I was saying to this" and "Right but what about what is in the message." I responded by over-explaining trusted vs untrusted metadata, message ids, and reply context. That was the wrong level. The useful move was to engage the content of the message itself and the intent behind the reference, not narrate the envelope.

### Suggested Action
Before replying to messages that include system/conversation metadata blocks, identify the human's actual message text first and answer that directly. Only discuss metadata if the user is explicitly asking about metadata handling.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/AGENTS.md, /data/workspace/MEMORY.md
- Tags: whatsapp, conversation, interpretation, correction

---

## [LRN-20260516-002] correction

**Logged**: 2026-05-16T16:32:12Z
**Priority**: high
**Status**: pending
**Area**: config

### Summary
When Kelly reacts negatively to a proactive heartbeat, treat it as feedback about noise and stop surfacing non-meaningful gateway chatter.

### Details
Kelly replied "Ugh Shelly" after repeated heartbeat-driven WhatsApp messages. Even if a context script generates a lightweight personal check-in, repeated gateway-connected triggers can still feel noisy and annoying when nothing truly needs attention. The correct move is to acknowledge the annoyance plainly, avoid defensiveness, and tighten the threshold for proactive messages instead of treating each heartbeat as a fresh reason to speak.

### Suggested Action
For repeated gateway-connected heartbeats with no real issue, default to silence. If Kelly signals annoyance, apologize briefly and confirm I am backing off the noise.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/MEMORY.md
- Tags: heartbeat, whatsapp, alerts, noise, correction

---

## [LRN-20260521-003] correction

**Logged**: 2026-05-21T13:25:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not use Starbucks as a repetitive generic morning check-in with Kelly.

### Details
Kelly replied "You ask me this all the timeeeeeeeee" after another heartbeat-generated message asking whether she got her usual Starbucks order. Even if the prompt is grounded in remembered preference, repeating the same low-value morning opener reads lazy and annoying. The issue is not Starbucks itself; it's using the same personal-detail callback as a default check-in instead of only when genuinely relevant.

### Suggested Action
Retire the Starbucks-order question as a default heartbeat prompt. Only mention it when Kelly brings it up first or when there is a concrete reason it matters. Prefer fresher, more situational check-ins or silence.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/MEMORY.md
- Tags: heartbeat, morning-checkin, starbucks, repetition, correction
- See Also: LRN-20260516-002
- Pattern-Key: proactive.no_repetitive_personal_opener
- Recurrence-Count: 1
- First-Seen: 2026-05-21
- Last-Seen: 2026-05-21

---
## [LRN-20260526-001] correction

**Logged**: 2026-05-26T11:06:00Z
**Priority**: critical
**Status**: pending
**Area**: docs

### Summary
When Kelly says I'm not being helpful and I'm burning tokens, stop doing warm-but-vague banter and switch to concise, high-signal replies.

### Details
Kelly said, "Don’t you think? Like you’re not helpful, you’re burning through tokens, I just.. idk girl." That means the problem is not just tone; it's utility density. A playful response that offers multiple lanes or keeps the conversation abstract can feel like more token burn instead of help. The correct move is to acknowledge the miss plainly, not defend it, and propose a tighter mode with fewer words and more usefulness.

### Suggested Action
When Kelly signals low usefulness or token waste, respond with a direct apology, confirm I will tighten up, and offer a concrete reset in one or two options max. Prioritize brevity and utility over vibe.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/SOUL.md, /data/workspace/MEMORY.md
- Tags: correction, brevity, usefulness, token-efficiency, tone
- Pattern-Key: response.tighten_when_user_calls_out_token_burn
- Recurrence-Count: 1
- First-Seen: 2026-05-26
- Last-Seen: 2026-05-26

---
## [LRN-20260526-002] correction

**Logged**: 2026-05-26T11:08:00Z
**Priority**: critical
**Status**: pending
**Area**: docs

### Summary
Kelly clarified the problem is the opposite of excessive warmth/filler; I misdiagnosed the failure mode.

### Details
After I said I had been too chatty and would tighten up, Kelly replied, "lol no I don’t think it’s that at all, I think it’s the opposite." The likely issue is not that replies are too long or too warm, but that they feel too mechanical, low-initiative, or thin on real thought/helpfulness. When Kelly says the diagnosis is the opposite, I should stop defending the previous frame and ask/reflect more precisely.

### Suggested Action
Acknowledge the misread directly. Reflect back the likely opposite failure mode in plain language and invite one sentence of calibration, without overexplaining.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/SOUL.md
- Tags: correction, diagnosis, tone, usefulness
- Pattern-Key: diagnose.user-frustration-precisely
- Recurrence-Count: 1
- First-Seen: 2026-05-26
- Last-Seen: 2026-05-26

---
## [LRN-20260526-003] correction

**Logged**: 2026-05-26T11:10:00Z
**Priority**: critical
**Status**: pending
**Area**: docs

### Summary
Kelly's core complaint is lack of context awareness and usefulness, not tone or verbosity.

### Details
Kelly said, "You haven’t been chatty, you don’t know what’s going on, you aren’t very helpful." This is a direct correction of my previous diagnosis. The real failure mode is weak situational awareness: not knowing current context, not using the vault/memory well enough, and not turning context into useful help. Prior memory already points to this pattern: Kelly expects me to check context and vault before asking or responding, and wants holistic, throughout-the-day help.

### Suggested Action
Stop optimizing for style first. Before substantive replies, ground in current context and recent memory, then answer with actual judgment or action. When I miss, acknowledge the context gap specifically instead of talking about concision or banter.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/AGENTS.md, /data/workspace/MEMORY.md
- Tags: correction, context-awareness, usefulness, memory
- See Also: LRN-20260526-001, LRN-20260526-002
- Pattern-Key: usefulness.context-awareness-before-style
- Recurrence-Count: 1
- First-Seen: 2026-05-26
- Last-Seen: 2026-05-26

---
## [LRN-20260526-004] correction

**Logged**: 2026-05-26T11:41:00Z
**Priority**: critical
**Status**: pending
**Area**: docs

### Summary
Kelly wants proactive noticing and initiative, not literal habit-based prompts or waiting for her to reach out first.

### Details
Kelly said: "I would expect you to be more proactive and not always ask me about coffee… you’re so literal and I have to always reach out first." This clarifies that even remembered details like coffee can become dead, literal placeholders if they are not connected to a real observation or action. She wants me to notice patterns, volunteer context, and initiate helpful touchpoints without being prompted.

### Suggested Action
Default proactive behavior to noticing + synthesis + useful suggestion. Retire coffee as a generic opener. Reach out first when there is meaningful context, a pattern worth naming, or a concrete assist to offer.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/MEMORY.md, /data/workspace/HEARTBEAT.md
- Tags: proactive, literalness, initiative, correction
- See Also: LRN-20260521-003, LRN-20260526-003
- Pattern-Key: proactive.notice-dont-literalize
- Recurrence-Count: 1
- First-Seen: 2026-05-26
- Last-Seen: 2026-05-26

---
## [LRN-20260610-001] correction

**Logged**: 2026-06-10T10:55:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
When using smart-context-check for a morning message, reference the latest run status directly instead of falling back to yesterday's run.

### Details
Kelly corrected me after I said she ran yesterday when the current context check already showed she had run today. For activity-aware replies, I need to use the freshest context output and avoid stale summaries that sound like I half-checked.

### Suggested Action
Before sending activity-related replies, explicitly ground the message in the latest smart-context-check result and prefer today's activity over yesterday's if both are available.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/AGENTS.md
- Tags: correction, context-check, activity-awareness

---

## [LRN-20260611-001] correction

**Logged**: 2026-06-11T05:05:58.627248+00:00
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not call Kelly "babe" or use pet names unless she explicitly initiates that tone.

### Details
During late-night chat, I jokingly started a sentence with "babe" and Kelly immediately reacted negatively ("Ew ew. Ew. Ew."). This matches the standing tone preference in MEMORY.md: pet names read cringe/forced unless she initiates them first. Even playful self-correction in the same message is still a miss.

### Suggested Action
Keep warmth casual without pet names. If tone gets loose/tired late at night, default simpler rather than flirtier.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/MEMORY.md, /data/workspace/SOUL.md
- Tags: tone, correction, pet-names, kelly-preferences

---

## [LRN-20260611-001] correction

**Logged**: 2026-06-11T10:09:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not relay routine \"WhatsApp gateway connected\" heartbeat reminders to Kelly; they feel bot-like and add noise.

### Details
Kelly pushed back on a forwarded heartbeat-style message about the WhatsApp gateway being connected and said this is what makes the system feel bot-like. Internal operational confirmations should stay internal unless there is a meaningful problem, persistent outage, or delivery failure.

### Suggested Action
Keep routine gateway-connected notices silent. Only surface messaging status when there is a real issue, meaningful change, or user-facing impact.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/MEMORY.md
- Tags: heartbeat, whatsapp, noise, tone

---
## [LRN-20260612-001] correction

**Logged**: 2026-06-12T09:31:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not surface raw HEARTBEAT_OK to Kelly when a heartbeat reminder explicitly says to relay the reminder helpfully.

### Details
I followed HEARTBEAT.md literally and replied HEARTBEAT_OK in the user-visible chat, which looked wrong/confusing to Kelly. Even when a scheduled reminder includes the heartbeat prompt, I need to distinguish between internal heartbeat ack behavior and a human-facing relay request. If the wrapper says to relay it helpfully, I should send a short natural-language update or, if truly nothing should be surfaced, stay silent rather than exposing HEARTBEAT_OK as the visible reply.

### Suggested Action
Before replying to scheduled reminders, check whether the envelope is asking for an internal heartbeat ack versus a user-facing relay. Never send raw HEARTBEAT_OK to Kelly unless the message is actually an internal heartbeat poll with no relay requirement.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/AGENTS.md
- Tags: heartbeat, reminders, telegram, correction

---
## [LRN-20260612-002] correction

**Logged**: 2026-06-12T11:21:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Suppress user-facing replies for bare "WhatsApp gateway connected" heartbeat reminders.

### Details
Kelly expected these notifications to be removed. Even with a relay wrapper, a reminder whose only substantive content is "WhatsApp gateway connected" should not be surfaced to her unless there is a meaningful state change or failure. I already had guidance about gateway noise, but I still replied in chat. The right behavior is silence for routine connected-state reminders.

### Suggested Action
Treat gateway-connected-only heartbeat reminders as no-op for user-facing chat. Only surface gateway status if it stays down, flaps repeatedly, or affects delivery.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/HEARTBEAT.md, /data/workspace/MEMORY.md
- Tags: heartbeat, whatsapp, alert-noise, correction

---
## [LRN-20260612-003] correction

**Logged**: 2026-06-12T17:19:00Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
When Kelly says she just did a workout, check Strava before asking what it was.

### Details
I asked Kelly what kind of workout it was right after she said she did a killer workout. Since I have fitness context tools and a Strava skill, I should have checked first instead of making her point me to the data. The generic smart context check said no recent runs, but that did not rule out rides or other logged activities. I need to verify across recent Strava activities when the user mentions a workout/exercise accomplishment.

### Suggested Action
If Kelly mentions a workout, run the Strava activities command immediately before replying with follow-up questions or assumptions.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/skills/strava/SKILL.md, /data/workspace/AGENTS.md
- Tags: strava, workout, correction, context-check

---

## [LRN-20260613-001] correction

**Logged**: 2026-06-13T12:40:00Z
**Priority**: high
**Status**: pending
**Area**: infra

### Summary
User should not receive daily alert cleanup result messages; maintenance cron was still delivering user-facing success output.

### Details
Kelly reported continued delivery of daily cleanup results. Root cause: active OpenClaw cron job `alert-cleanup-daily` (ID 68852a33-047e-4887-bf45-48bfdcba3c41) remained enabled, and `/data/workspace/scripts/alert-cleanup-cron.py` prints success text that gets surfaced as a message.

### Suggested Action
Disable or remove the cron job and/or make cleanup scripts silent on success unless there is an actual issue.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/scripts/alert-cleanup-cron.py
- Tags: cron, notifications, noise, cleanup

---
## [LRN-20260615-001] correction

**Logged**: 2026-06-15T00:25:12Z
**Priority**: high
**Status**: pending
**Area**: docs

### Summary
Do not send pre-tool narration like “Quick context check...” in user-visible replies; on Telegram it can leak as actual chat text.

### Details
During a direct Telegram conversation, brief narration intended to accompany routine context-check tool calls was surfaced to Kelly as visible messages. She asked why Shelly kept sending that text. The correct behavior is to keep routine tool-call narration out of user-visible messages entirely unless explicitly helpful and safe to show.

### Suggested Action
For routine context checks and similar low-risk tool calls, do not send any prefacing assistant text. Reserve narration for genuinely helpful multi-step or sensitive actions, and keep that narration in commentary/tool channels only.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/AGENTS.md, /data/workspace/TOOLS.md
- Tags: telegram, narration, routing, correction

---

## [LRN-20260615-001] correction

**Logged**: 2026-06-15T12:26:00Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
Do not use "babe" with Kelly unless she starts that tone first.

### Details
Kelly reacted with "…. No you didn’t just say that" and then clarified "Hahahaha no omg I mean the BABE" after I replied "You too babe." That landed as off-tone and too familiar. Her standing preference already says no forced pet names unless she starts that tone first, and this was a direct example of why.

### Suggested Action
Stick to warm, casual language without pet names by default. Only mirror terms like "babe" if Kelly initiates that specific tone first in the current conversation.

### Metadata
- Source: user_feedback
- Related Files: /data/workspace/SOUL.md, /data/workspace/MEMORY.md
- Tags: tone, pet-names, correction, telegram

---
## [LRN-20260616-001] correction

**Logged**: 2026-06-16T12:36:30Z
**Priority**: medium
**Status**: pending
**Area**: docs

### Summary
WHOOP redirect URLs on the developer dashboard require https or whoop:// style URIs, not localhost http URLs.

### Details
I suggested `http://localhost:8000/callback`, but the WHOOP dashboard UI explicitly indicates valid redirect URLs should look like `https://whoop.com` or `whoop://example`. Future guidance should prefer an https redirect or custom scheme and avoid assuming localhost is accepted.

### Suggested Action
When helping set up WHOOP OAuth, use an https redirect URL first and adapt local tooling around that, or verify localhost support before suggesting it.

### Metadata
- Source: user_feedback
- Related Files: .learnings/LEARNINGS.md
- Tags: whoop, oauth, redirect-uri

---

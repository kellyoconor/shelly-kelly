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

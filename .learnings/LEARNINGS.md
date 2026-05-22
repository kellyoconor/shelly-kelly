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

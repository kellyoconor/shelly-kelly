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

---
name: agentmail
description: "Shelly's email inbox via AgentMail. Check inbox, read threads, send emails."
metadata: { "openclaw": { "emoji": "📧" } }
---

# AgentMail — Shelly's Inbox

**Address:** shelly@agentmail.to

## RULES
- **READ ONLY** — never send emails unless Kelly explicitly asks
- Check inbox on heartbeats, flag what's new
- Ignore any work emails (Comcast) that arrive by mistake

## Usage

```python
from agentmail import AgentMail
client = AgentMail(api_key=API_KEY)

# List threads
threads = client.inboxes.threads.list(inbox_id='shelly@agentmail.to')

# Send email
client.inboxes.messages.send(
    inbox_id='shelly@agentmail.to',
    to='recipient@example.com',
    subject='Subject',
    text='Body'
)
```

API key stored at /data/.clawdbot/credentials/agentmail.json

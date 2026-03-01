---
name: google-calendar
description: "Read-only Google Calendar access via OAuth. View today's events, weekly schedule, upcoming appointments."
metadata: { "openclaw": { "emoji": "📅", "requires": { "env": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "GOOGLE_REFRESH_TOKEN"] } } }
---

# Google Calendar (Read-Only)

Read-only access to Kelly's calendar via a dedicated Google account with OAuth.

## Commands

```bash
python3 scripts/calendar.py today    # Today's events
python3 scripts/calendar.py week     # Next 7 days
python3 scripts/calendar.py raw [N]  # Raw JSON, next N days
```

## Rules
- **READ ONLY** — never attempt to create, edit, or delete events
- Use in morning briefings to preview the day
- Mention upcoming events proactively when relevant
- Don't share calendar details in group chats

## Setup
- OAuth credentials stored in env (survive redeploys)
- Token auto-refreshes, no manual intervention needed
- Kelly controls what's visible via her dedicated Google account

---
name: mirror
description: "The Mirror: reflective morning question based on health, fitness, and calendar data"
metadata: { "openclaw": { "emoji": "🪞", "requires": { "bins": ["python3"] } } }
---

# The Mirror

Generates ONE reflective, introspective question for Kelly's morning briefing by analyzing health, fitness, and calendar data.

## Commands

```bash
python3 scripts/mirror.py                    # Generate today's question
python3 scripts/mirror.py --snapshot-only    # Just save today's data snapshot
python3 scripts/mirror.py --trends           # Show current trend observations
```

## Data Sources

- **Oura Ring** — sleep, readiness, HRV, resting HR via `skills/oura/scripts/oura.py brief`
- **Strava** — recent runs and training load via `skills/strava/scripts/strava.py`
- **Google Calendar** — today's schedule density via `skills/google-calendar/scripts/calendar.py`

## How It Works

1. Pulls today's data from all three sources
2. Saves a daily snapshot to `data/snapshots/YYYY-MM-DD.json`
3. Compares against historical snapshots for trends (7+ days = weekly, 30+ days = monthly)
4. Generates one rule-based reflective question informed by the data patterns
5. Never prescriptive — always open-ended and introspective

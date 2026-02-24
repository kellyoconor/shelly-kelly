---
name: oura
description: "Oura Ring health data: sleep, readiness, HRV, heart rate, activity. Use when the user asks about sleep quality, recovery, readiness score, HRV, resting heart rate, or daily health metrics."
metadata: { "openclaw": { "emoji": "💍", "requires": { "bins": ["python3"] } } }
---

# Oura Ring

Pull sleep, readiness, and health data from Oura's API. Scripts in `scripts/`.

## Commands

```bash
python3 scripts/oura.py brief [date]        # Combined daily summary (default: yesterday)
python3 scripts/oura.py sleep [date]         # Detailed sleep data
python3 scripts/oura.py readiness [date]     # Readiness score + contributors
python3 scripts/oura.py activity [date]      # Daily activity
python3 scripts/oura.py heartrate [date]     # HR summary
python3 scripts/oura.py info                 # Personal info
```

Date format: YYYY-MM-DD. Defaults to yesterday for sleep/readiness, today for activity.

## Daily brief

`brief` combines sleep + readiness + activity into one call. Includes total sleep hours, deep/REM breakdown, efficiency, HRV, lowest HR, and readiness score.

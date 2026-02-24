---
name: strava
description: Strava running and fitness data. Use when the user asks about runs, training, mileage, pace, weekly summary, race prep, or any fitness/running data from Strava.
metadata: { "openclaw": { "emoji": "🏃‍♀️", "requires": { "bins": ["python3"] } } }
---

# Strava

Pull running and fitness data from Strava's API. Scripts in `scripts/`.

## Commands

```bash
python3 scripts/strava.py runs [count]     # Recent runs
python3 scripts/strava.py weekly           # This week's summary
python3 scripts/strava.py stats            # All-time stats
python3 scripts/strava.py activities [n]   # All activity types
python3 scripts/strava.py activity <id>    # Single activity detail
python3 scripts/strava.py athlete          # Profile
```

Kelly uses miles and min/mi pace.

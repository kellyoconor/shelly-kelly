# Morning Briefing Cron Fix — 2026-05-28

## What broke
The 6:30 AM "Kelly's morning briefing" cron job was configured as a `main` session `systemEvent` with reminder text.

That meant the scheduler injected instructions into chat instead of actually executing the morning briefing workflow.

## Symptom
At 6:30 AM, Kelly received a reminder-style message telling the agent to run:
- `python3 /data/workspace/scripts/morning-briefing.py`
- send the output to WhatsApp
- run `python3 /data/workspace/scripts/morning-briefing.py --append-daily-note`

Instead of doing those steps, the system surfaced the reminder text itself.

## Root cause
The job used:
- `sessionTarget: main`
- `payload.kind: systemEvent`

That is appropriate for nudges/reminders, but not for a job that needs to execute commands and deliver output.

## Live fix applied
Updated cron job `cf5d26ec-ffc7-41b6-be1e-ee80552b0035` (`Kelly's morning briefing`) to:

- `sessionTarget: isolated`
- `payload.kind: agentTurn`
- `delivery.mode: announce`
- `delivery.channel: whatsapp`
- `delivery.to: +13018302401`

New runtime behavior:
1. Run `python3 /data/workspace/scripts/morning-briefing.py`
2. Run `python3 /data/workspace/scripts/morning-briefing.py --append-daily-note`
3. Return only the briefing output for delivery

## Recovery step taken
After updating the cron job, the morning briefing was run manually once so Kelly still received today's briefing.

## Why this file exists
Cron updates are live config changes and do not automatically produce a git commit.
This note creates a repo-visible paper trail for the fix.

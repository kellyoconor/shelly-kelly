# Shelly Proactive Presence Test Plan

## Goal
Prove the proactive-presence system behaves correctly, not just that scripts run.

## Core principle
Every change should be validated at three levels:
1. **Syntax / compile**
2. **Behavioral assertion**
3. **State/output verification**

## Repeatable script
Primary quick-run test script:
- `/data/workspace/scripts/test-proactive-presence.sh`

Run with:
```bash
sh /data/workspace/scripts/test-proactive-presence.sh
```

## Current assertions covered

### 1. Quality gate
- Literal proactive opener is blocked
- Substantive proactive message is allowed

### 2. Follow-up lifecycle
- Add follow-up
- Choose next follow-up
- Mark follow-up surfaced
- Reopen surfaced follow-up after resurfacing window
- Resolve follow-up

### 3. Follow-up auto-capture
- Noise/system summary is ignored
- Meaningful unresolved summary creates a follow-up

### 4. State integration
- Open follow-up appears in `kelly-state-check.py compact`

## Manual/extended checks still required

### A. Heartbeat behavior
- Heartbeat with weak/literal generated prompt should stay quiet
- Heartbeat with real context should only send if quality gate passes
- Gateway reconnect noise should not become a personal check-in

### B. Proactive sender behavior
- `kelly-aware-message.py` blocks weak message
- `proactive-kelly-message.sh` blocks weak message
- Shared validator remains the single source of truth

### C. Kelly State synthesis
Verify that focus prioritizes, in order:
1. open loops
2. active projects
3. recent focus
4. daily-note fallback

### D. Repetition control
- Follow-up should not surface repeatedly in a tight loop
- Resolved follow-up should disappear from active context
- Stale follow-up should not dominate focus state

## Known nuance
If `KELLY_FOLLOWUPS_RESURFACE_HOURS=0`, a surfaced follow-up reopens immediately when lifecycle rules are applied. That is expected behavior for testing the reopen path, but it means `list surfaced` will not stay surfaced under that setting.

## Definition of tested-enough for a commit
Before committing proactive-presence work:
- compile checks pass
- quick-run test script passes
- changed output/state inspected directly
- if behavior changed, at least one positive and one negative case verified

# Combined Context Scenario Test Plan

## Goal
Exercise heartbeat/context message generation using deterministic fixtures instead of live external services.

## Script
- `/data/workspace/scripts/test-combined-context-scenarios.sh`

Run with:
```bash
sh /data/workspace/scripts/test-combined-context-scenarios.sh
```

## Scenarios covered
1. No meaningful signal -> stay quiet
2. Bad significance-only message -> blocked by shared quality gate
3. Good significance-only message -> allowed
4. Mixed/recovery-aware health synthesis message -> allowed
5. Strong/available health synthesis message -> allowed
6. Run synthesis message -> allowed
7. Recent active conversation -> suppress proactive output

## Fixture hooks used
`combined-context-check.py` now supports:
- `COMBINED_CONTEXT_EXTERNAL_FIXTURE`
- `COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE`
- `COMBINED_CONTEXT_RECENT_STATE_JSON`
- `COMBINED_CONTEXT_CONVERSATION_JSON`

These should only be used for testing.

## Key bug fixed by this plan
Previously, if external context failed but significance returned a message, that significance message could bypass the shared quality gate. Scenario #2 now guards against regression.

## Definition of done for heartbeat/context changes
- compile check passes
- combined context scenario script passes
- at least one negative case and one positive case for the changed path
- no edge-case bypass of the shared quality gate

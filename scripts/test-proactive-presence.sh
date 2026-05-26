#!/bin/sh
set -eu

WORKDIR=/data/workspace
TMP_FOLLOWUPS=$(mktemp)
cleanup() {
  rm -f "$TMP_FOLLOWUPS"
}
trap cleanup EXIT INT TERM

printf '{"updated_at":null,"items":[]}' > "$TMP_FOLLOWUPS"

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

cd "$WORKDIR"

python3 -m py_compile \
  scripts/message_quality_gate.py \
  scripts/kelly_message_pipeline.py \
  scripts/ai-message-wrapper.py \
  scripts/kelly-aware-message.py \
  scripts/kelly-followups.py \
  scripts/kelly-state-check.py \
  scripts/update-kelly-state.py || fail "python compile"
pass "python compile"

if python3 scripts/message_quality_gate.py "Did you get your usual Starbucks order this morning? ☕" >/dev/null 2>&1; then
  fail "literal prompt should be blocked"
fi
pass "literal prompt blocked"

python3 scripts/message_quality_gate.py "You ran 6.02 yesterday and slept well, which suggests the floor is steadier than the vibe. Might help to protect momentum instead of overthinking the day." >/dev/null 2>&1 || fail "substantive prompt should pass"
pass "substantive prompt allowed"

if python3 scripts/kelly_message_pipeline.py validate "Did you get your usual Starbucks order this morning? ☕" >/dev/null 2>&1; then
  fail "shared pipeline should block literal prompt"
fi
pass "shared pipeline blocks literal prompt"

python3 scripts/kelly_message_pipeline.py validate "You ran 6.02 yesterday and slept well, which suggests the floor is steadier than the vibe. Might help to protect momentum instead of overthinking the day." >/dev/null 2>&1 || fail "shared pipeline should allow substantive prompt"
pass "shared pipeline allows substantive prompt"

if python3 scripts/message-interceptor.py validate message send --to "+[REDACTED_CLIENT_ID]401" --message "Did you get your usual Starbucks order this morning? ☕" >/dev/null 2>&1; then
  fail "message interceptor should block literal prompt"
fi
pass "message interceptor blocks literal prompt"

python3 scripts/message-interceptor.py validate message send --to "+[REDACTED_CLIENT_ID]401" --message "You ran 6.02 yesterday and slept well, which suggests the floor is steadier than the vibe. Might help to protect momentum instead of overthinking the day." >/dev/null 2>&1 || fail "message interceptor should allow substantive prompt"
pass "message interceptor allows substantive prompt"

export KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS"
export KELLY_FOLLOWUPS_RESURFACE_HOURS=24
python3 scripts/kelly-followups.py add "Test Loop" "Something to follow up on" emotional high >/dev/null || fail "follow-up add"
python3 scripts/kelly-followups.py next | grep -q '"topic": "Test Loop"' || fail "follow-up next"
pass "follow-up add/next"

python3 scripts/kelly-followups.py surfaced fu-001 >/dev/null || fail "mark surfaced"
python3 scripts/kelly-followups.py list surfaced | grep -q '"status": "surfaced"' || fail "surfaced status"
pass "follow-up surfaced"

export KELLY_FOLLOWUPS_RESURFACE_HOURS=0
python3 scripts/kelly-followups.py list open | grep -q '"status": "open"' || fail "reopen after resurfacing window"
pass "follow-up reopen after window"

python3 scripts/kelly-followups.py resolve fu-001 >/dev/null || fail "resolve follow-up"
python3 scripts/kelly-followups.py list resolved | grep -q '"status": "resolved"' || fail "resolved state"
pass "follow-up resolve"

printf '{"updated_at":null,"items":[]}' > "$TMP_FOLLOWUPS"
KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/followup-extractor.py "Heartbeat ran after WhatsApp gateway connected; no urgent issues surfaced." | grep -q '^{}$' || fail "extractor noise suppression"
pass "extractor noise suppression"

KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/followup-extractor.py "Kelly is conflicted about whether to keep pushing this system work tonight." --apply >/dev/null || fail "extractor apply"
KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/kelly-followups.py list open | grep -q 'whether to keep pushing this system work tonight' || fail "extractor captured follow-up"
pass "extractor captured follow-up"

printf '{"updated_at":null,"items":[{"id":"fu-009","topic":"State Test","note":"Check state integration","kind":"general","priority":"medium","status":"open","created_at":"2026-05-26T10:00:00","last_seen":"2026-05-26T10:00:00","last_surfaced":null,"times_surfaced":0,"resolved_at":null,"stale_at":null}]}' > "$TMP_FOLLOWUPS"
KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/kelly-state-check.py compact | grep -q 'Open loops: State Test: Check state integration' || fail "state integration"
pass "state integration"

KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/kelly-state-check.py compact | grep -q 'Avoid: Calendar Auth Issues' || fail "avoid topics surfaced"
pass "avoid topics surfaced"

printf '{"updated_at":null,"items":[{"id":"fu-011","topic":"Low Priority","note":"older and lower priority","kind":"general","priority":"low","status":"open","created_at":"2026-05-25T10:00:00","last_seen":"2026-05-25T10:00:00","last_surfaced":null,"times_surfaced":0,"resolved_at":null,"stale_at":null},{"id":"fu-012","topic":"High Priority","note":"more urgent and recent","kind":"general","priority":"high","status":"open","created_at":"2026-05-26T11:00:00","last_seen":"2026-05-26T11:30:00","last_surfaced":null,"times_surfaced":0,"resolved_at":null,"stale_at":null}]}' > "$TMP_FOLLOWUPS"
KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/kelly-followups.py next | grep -q '"topic": "High Priority"' || fail "priority ordering"
pass "priority ordering"

printf '{"updated_at":null,"items":[{"id":"fu-010","topic":"Repeat Test","note":"Should stay hidden while surfaced","kind":"general","priority":"medium","status":"surfaced","created_at":"2026-05-26T10:00:00","last_seen":"2026-05-26T10:00:00","last_surfaced":"2999-05-26T10:00:00","times_surfaced":1,"resolved_at":null,"stale_at":null}]}' > "$TMP_FOLLOWUPS"
KELLY_FOLLOWUPS_FILE="$TMP_FOLLOWUPS" python3 scripts/kelly-state-check.py compact | grep -q 'Repeat Test' && fail "surfaced follow-up should not appear before reopen window"
pass "surfaced follow-up stays hidden before reopen"

echo "All proactive presence tests passed."

#!/bin/sh
set -eu

WORKDIR=/data/workspace
TMPDIR=$(mktemp -d)
cleanup() {
  rm -rf "$TMPDIR"
}
export PROACTIVE_LOG_FILE="$TMPDIR/proactive-log.jsonl"
export PROACTIVE_STATE_FILE="$TMPDIR/proactive-state.json"
: > "$PROACTIVE_LOG_FILE"
trap cleanup EXIT INT TERM

pass() { echo "PASS: $1"; }
fail() { echo "FAIL: $1"; exit 1; }

cd "$WORKDIR"

printf '{"recent_activity": false, "negative_sentiment": false}' > "$TMPDIR/recent.json"
printf '{"error": "no external"}' > "$TMPDIR/external-error.json"
printf '{"no_significance": true}' > "$TMPDIR/significance-none.json"
printf '{"significance_message": "Did you get your usual Starbucks order this morning? ☕"}' > "$TMPDIR/significance-bad.json"
printf '{"significance_message": "You ran 6.02 yesterday and slept well, which suggests the floor is steadier than the vibe. Might help to protect momentum instead of overthinking the day."}' > "$TMPDIR/significance-good.json"
printf '{"health": "⚖️ 73%% ready 😴 90%% sleep", "running": "⏳ Yesterday: 2026-05-25, 6.02mi"}' > "$TMPDIR/external-health-mixed.json"
printf '{"health": "💪 91%% ready", "running": "⏳ Earlier this week: 2026-05-23, 5.00mi"}' > "$TMPDIR/external-health-strong.json"
printf '{"run_today": "✅ Ran today: 7.03mi at 8:42/mi"}' > "$TMPDIR/external-run.json"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-error.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-none.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out1.txt"
[ ! -s "$TMPDIR/out1.txt" ] || fail "combined context should stay quiet with no meaningful signal"
pass "combined context stays quiet with no meaningful signal"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-error.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-bad.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out2.txt"
[ ! -s "$TMPDIR/out2.txt" ] || fail "bad significance message should be blocked"
pass "bad significance message blocked"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-error.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-good.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out3.txt"
grep -q 'protect momentum instead of overthinking the day' "$TMPDIR/out3.txt" || fail "good significance message should pass"
pass "good significance message allowed"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-health-mixed.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-none.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out4.txt"
grep -q 'protect-your-energy day than a prove-something day' "$TMPDIR/out4.txt" || fail "mixed health synthesis should pass"
pass "mixed health synthesis allowed"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-health-strong.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-none.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out5.txt"
grep -q 'structure will probably work better than hesitation' "$TMPDIR/out5.txt" || fail "strong health synthesis should pass"
pass "strong health synthesis allowed"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-run.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-none.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": false, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out6.txt"
grep -q 'protect that instead of negotiating with it' "$TMPDIR/out6.txt" || fail "run synthesis should pass"
pass "run synthesis allowed"

: > "$PROACTIVE_LOG_FILE"
rm -f /data/workspace/memory/heartbeat-state.json
COMBINED_CONTEXT_EXTERNAL_FIXTURE="$TMPDIR/external-run.json" \
COMBINED_CONTEXT_SIGNIFICANCE_FIXTURE="$TMPDIR/significance-none.json" \
COMBINED_CONTEXT_RECENT_STATE_JSON='{"recent_activity": true, "negative_sentiment": false}' \
COMBINED_CONTEXT_CONVERSATION_JSON='{"running": false, "health_data": false, "calendar": false, "current_work": false, "morning_routine": false}' \
python3 scripts/combined-context-check.py > "$TMPDIR/out7.txt"
[ ! -s "$TMPDIR/out7.txt" ] || fail "recent active conversation should suppress proactive output"
pass "recent activity suppresses proactive output"

echo "All combined-context scenario tests passed."

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
python3 -m py_compile scripts/proactive_presence.py scripts/combined-context-check.py || fail "python compile milestone2"
pass "python compile milestone2"

python3 - <<'PY' > "$TMPDIR/followup.txt"
import importlib.util
spec = importlib.util.spec_from_file_location('combined', '/data/workspace/scripts/combined-context-check.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
state = "Physical: Kelly ran 5.12 miles yesterday. Kelly's readiness is moderate at 70% and her sleep was restless last night (58%).\nSchedule: Kelly's calendar authentication has expired.\nFocus: Active project energy: Shelly Proactive Presence Spec - Telegram First is live right now.\nTone: The recent tone looks clear and relatively grounded.\nOpen loops: decide whether to keep pushing this system work tonight\nAvoid: Calendar Auth Issues | NWSL Interview"
items = mod.build_proactive_candidates({}, {}, {'running': False, 'health_data': False}, state, 14)
print(items)
PY
grep -q 'followup' "$TMPDIR/followup.txt" || fail "followup candidate should be generated"
grep -q 'close the gap instead of letting it keep humming in the background' "$TMPDIR/followup.txt" || fail "followup message should contain proactive assist angle"
pass "followup candidate generated"

python3 - <<'PY' > "$TMPDIR/assist.txt"
import importlib.util
spec = importlib.util.spec_from_file_location('combined', '/data/workspace/scripts/combined-context-check.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
state = "Physical: Kelly ran 5.12 miles yesterday. Kelly's readiness is moderate at 70% and her sleep was restless last night (58%).\nSchedule: Kelly's calendar authentication has expired.\nFocus: Active project energy: Shelly Proactive Presence Spec - Telegram First is live right now.\nTone: The recent tone looks clear and relatively grounded.\nAvoid: Calendar Auth Issues | NWSL Interview"
items = mod.build_proactive_candidates({}, {}, {'running': False, 'health_data': False}, state, 14)
print(items)
PY
grep -q 'practical_assist' "$TMPDIR/assist.txt" || fail "project assist candidate should be generated"
pass "project assist candidate generated"

python3 - <<'PY' > "$TMPDIR/repeat.json"
from scripts.proactive_presence import build_snapshot, evaluate_snapshot, log_decision
snapshot1 = build_snapshot(
    external_events={}, significance_result={}, conversation_check={},
    kelly_state_text='Physical: Kelly ran 5.12 miles yesterday. Kelly\'s readiness is moderate at 70% and her sleep was restless last night (58%).',
    recent_activity={'recent_activity': False, 'negative_sentiment': False},
    candidates=[{'source':'pattern','message_mode':'pattern_notice','message':'Quick read: Kelly ran 5.12 miles yesterday. Kelly\'s readiness is moderate at 70% and her sleep was restless last night (58%). I don\'t think this needs a big intervention — just a useful nudge to keep the day from getting away from you. Want me to turn that into a low-lift next step?','why_now':'test','confidence':0.7,'min_gap_hours':0}]
)
decision1 = evaluate_snapshot(snapshot1)
log_decision(snapshot1, decision1)
snapshot2 = build_snapshot(
    external_events={}, significance_result={}, conversation_check={},
    kelly_state_text='Physical: Kelly ran 5.12 miles yesterday. Kelly\'s readiness is moderate at 70% and her sleep was restless last night (58%).',
    recent_activity={'recent_activity': False, 'negative_sentiment': False},
    candidates=[{'source':'pattern','message_mode':'pattern_notice','message':'Quick read: Kelly ran 5.12 miles yesterday. Kelly\'s readiness is moderate at 70% and her sleep was restless last night (58%). I don\'t think this needs a big intervention — just a useful nudge to keep the day from getting away from you. Want me to turn that into a low-lift next step?','why_now':'test','confidence':0.7,'min_gap_hours':0}]
)
print(evaluate_snapshot(snapshot2))
PY
grep -q "'decision': 'suppress'" "$TMPDIR/repeat.json" || fail "repeat candidate should be suppressed after prior send"
pass "repeat suppression works"

echo "All milestone 2 tests passed."

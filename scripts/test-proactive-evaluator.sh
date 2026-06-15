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
python3 -m py_compile scripts/proactive_presence.py || fail "python compile proactive_presence"
pass "python compile proactive_presence"

python3 - <<'PY' > "$TMPDIR/out.json" || exit 1
import json
from scripts.proactive_presence import build_snapshot, evaluate_snapshot

snapshot = build_snapshot(
    external_events={'run_today': '✅ Ran today: 7.03mi at 8:42/mi'},
    significance_result={},
    conversation_check={'running': False, 'health_data': False},
    kelly_state_text='Physical: Kelly ran 5.12 miles yesterday. Kelly\'s readiness is moderate at 70% and her sleep was restless last night (58%).\nSchedule: Kelly\'s calendar authentication has expired.\nFocus: Active project energy: Shelly Proactive Presence Spec - Telegram First is live right now.\nTone: The recent tone looks clear and relatively grounded.\nAvoid: Calendar Auth Issues | NWSL Interview',
    recent_activity={'recent_activity': False, 'negative_sentiment': False},
    candidates=[{
        'source': 'run',
        'message_mode': 'body_training_read',
        'message': 'Nice work on your run — ✅ Ran today: 7.03mi at 8:42/mi. That usually means the day already has some momentum; protect that instead of negotiating with it.',
        'why_now': 'A recent run creates a clear momentum/protection angle right now.',
        'confidence': 0.8,
    }],
)
print(json.dumps(evaluate_snapshot(snapshot)))
PY

grep -q '"decision": "send"' "$TMPDIR/out.json" || fail "evaluator should approve strong candidate"
grep -q '"reason": "run"' "$TMPDIR/out.json" || fail "evaluator should preserve source reason"
pass "evaluator approves strong candidate"

python3 - <<'PY' > "$TMPDIR/out2.json" || exit 1
import json
from scripts.proactive_presence import build_snapshot, evaluate_snapshot

snapshot = build_snapshot(
    external_events={},
    significance_result={},
    conversation_check={'running': False, 'health_data': False},
    kelly_state_text='',
    recent_activity={'recent_activity': True, 'negative_sentiment': False},
    candidates=[{
        'source': 'run',
        'message_mode': 'body_training_read',
        'message': 'Nice work on your run — ✅ Ran today: 7.03mi at 8:42/mi. That usually means the day already has some momentum; protect that instead of negotiating with it.',
        'why_now': 'A recent run creates a clear momentum/protection angle right now.',
        'confidence': 0.8,
    }],
)
print(json.dumps(evaluate_snapshot(snapshot)))
PY

grep -q '"decision": "suppress"' "$TMPDIR/out2.json" || fail "recent active conversation should suppress send"
grep -q 'recent-active-conversation' "$TMPDIR/out2.json" || fail "suppression reason should be explicit"
pass "recent activity suppresses proactive send"

python3 - <<'PY' > "$TMPDIR/out3.json" || exit 1
import json
from scripts.proactive_presence import build_snapshot, evaluate_snapshot

snapshot = build_snapshot(
    external_events={},
    significance_result={},
    conversation_check={'running': False, 'health_data': False},
    kelly_state_text='',
    recent_activity={'recent_activity': False, 'negative_sentiment': False},
    candidates=[
        {
            'source': 'pattern',
            'message_mode': 'pattern_notice',
            'message': 'Quick read: your tone and focus both look a little scattered today, which suggests a small deliberate move would help more than drifting. Worth protecting the next hour instead of letting the day get mushy.',
            'why_now': 'Multiple real signals lined up, and enough quiet time has passed that a grounded nudge is justified.',
            'confidence': 0.95,
        },
        {
            'source': 'followup',
            'message_mode': 'emotional_follow_up',
            'message': 'You still have an open loop around the thing you were circling earlier, which feels like the kind of thing that quietly burns energy until you name the next move. If you want, I can help turn it into one clean next step right now.',
            'why_now': 'An open loop is still live and deserves proactive follow-through.',
            'confidence': 0.84,
        }
    ],
)
print(json.dumps(evaluate_snapshot(snapshot)))
PY

grep -q '"decision": "send"' "$TMPDIR/out3.json" || fail "ordered candidates should still produce a send"
grep -q '"reason": "followup"' "$TMPDIR/out3.json" || fail "followup should outrank weaker pattern notice"
pass "evaluator prioritizes followup over pattern"

python3 - <<'PY' > "$TMPDIR/out4.json" || exit 1
import json
from scripts.proactive_presence import build_snapshot, evaluate_snapshot

snapshot = build_snapshot(
    external_events={},
    significance_result={},
    conversation_check={'running': False, 'health_data': False},
    kelly_state_text='',
    recent_activity={'recent_activity': False, 'negative_sentiment': True},
    candidates=[{
        'source': 'pattern',
        'message_mode': 'pattern_notice',
        'message': 'Quick read: your tone and focus both look a little scattered today, which suggests a small deliberate move would help more than drifting. Worth protecting the next hour instead of letting the day get mushy.',
        'why_now': 'Multiple real signals lined up, and enough quiet time has passed that a grounded nudge is justified.',
        'confidence': 0.7,
    }],
)
print(json.dumps(evaluate_snapshot(snapshot)))
PY

grep -q '"decision": "suppress"' "$TMPDIR/out4.json" || fail "negative sentiment should suppress weak pattern nudges"
grep -q 'recent-negative-sentiment' "$TMPDIR/out4.json" || fail "negative sentiment suppression should be explicit"
pass "negative sentiment suppresses weak nudges"

echo "All proactive evaluator tests passed."

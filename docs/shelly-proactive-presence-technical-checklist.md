# Shelly Proactive Presence — Technical Checklist

## Goal
Translate the proactive-presence plan into concrete changes against the current OpenClaw workspace and scripts.

## Current system diagnosis

### 1. `scripts/combined-context-check.py` is still generating literal user-facing prompts
This is the main behavior bug.

Current examples in code:
- `"Did you get your usual Starbucks order this morning? ☕"`
- `"No run today - taking a rest day or just haven't gotten out there yet? 🏃‍♀️"`
- `"How's the Steely development going? Any breakthroughs today? 🤖"`
- direct health prompts that ask Kelly to do interpretation work

**Impact:**
The system can have valid input data and still emit low-value, literal, repetitive output.

### 2. `scripts/kelly-state-check.py` is too thin
It currently produces only:
- physical
- schedule
- focus

Missing:
- recent 2-3 day rhythm
- open loops
- emotional / contextual threads
- do-not-ask or repetition guardrails
- meaningful delta detection

**Impact:**
The state model is a status snapshot, not a relationship-aware context layer.

### 3. `scripts/update-kelly-state.py` only republishes thin state
It faithfully writes `kelly-state.md`, but the content itself is too limited.

**Impact:**
The pipeline updates state, but not enough state to meaningfully improve proactive behavior.

### 4. `scripts/ai-message-wrapper.py` updates state but does not quality-check the message
Current behavior:
- update Kelly state
- load it into context
- return

Missing:
- proactive vs reactive classification
- quality gate
- literal/repetitive pattern rejection
- required observation + interpretation + action structure

### 5. `HEARTBEAT.md` still allows check-in generation too early
Key line now:
- if personal check-in generated, send that message to Kelly and stop

**Impact:**
This delegates too much authority to generator scripts that still contain literal logic.

### 6. `scripts/message-interceptor.py` handles freshness, not substance
Useful for context freshness, but not enough to prevent weak messages.

---

## Implementation plan by file

## Phase 1 — Stop low-value proactive behavior immediately

### A. Edit `scripts/combined-context-check.py`
**Priority:** Critical

#### Remove / disable these literal branches
- morning Starbucks prompt
- generic no-run prompt
- generic current-work prompt
- generic health prompt that asks Kelly to do the synthesis

#### Replace with new output contract
`merge_contexts()` should return a structured result, not just a string. Example:

```python
{
  "message": "...",
  "kind": "pattern_notice",
  "signals": ["run_yesterday", "sleep_good", "mood_flat"],
  "quality": {
    "observation": True,
    "interpretation": True,
    "action": False
  },
  "safe_to_send": True
}
```

If that is too big a change for first pass, then simpler interim step:
- keep returning string
- but only generate strings that include at least two of: observation / interpretation / action
- otherwise return empty string

#### Add new gating helper
Create helper functions like:
- `is_literal_prompt(message)`
- `passes_quality_gate(message, metadata)`
- `is_repetitive_topic(topic)`

#### New message policy
Allowed proactive outputs should sound like:
- a pattern notice
- a useful read
- a follow-up on something live
- a practical assist

Not allowed:
- generic greetings
- coffee references as default intimacy
- questions about things the system already knows

---

### B. Tighten `HEARTBEAT.md`
**Priority:** Critical

#### Replace the current rule
Current:
- if personal check-in generated: send that message to Kelly and stop

#### New rule
Only send a proactive message if it is:
- non-literal
- non-repetitive
- context-grounded
- materially useful
- approved by the message quality gate

#### Add explicit negative examples
Add a section to HEARTBEAT.md that says heartbeat must not send:
- coffee openers
- generic how-are-you check-ins
- obvious activity questions the system can answer itself
- repetitive “saw your run” loops unless there is a genuinely new angle

---

### C. Add quality gate to `scripts/ai-message-wrapper.py`
**Priority:** Critical

#### New behavior
After loading Kelly state, the wrapper should optionally validate proposed proactive text before send.

Suggested approach:
- add a function like `validate_proactive_message(message_text)`
- reject if it matches literal patterns
- reject if it lacks enough substance
- optionally annotate why it passed/failed

#### Minimum validation rules
A proactive message should include at least two of:
- observation
- interpretation
- action

And should fail if it contains patterns like:
- `usual Starbucks`
- `how are you`
- `did you get coffee`
- `how was your day`
- `have you run yet`

#### Output behavior
If validation fails:
- log locally
- do not send
- default to silence

---

## Phase 2 — Build active Kelly context

### D. Create a new active context file
**Priority:** High

Create either:
- `/data/workspace/kelly-active-context.md`

or
- `/data/workspace/memory/active-kelly-context.json`

I recommend JSON for script use plus optional markdown render.

#### Proposed schema
```json
{
  "updated_at": "ISO-8601",
  "body": {
    "sleep_score": 90,
    "readiness_score": 73,
    "recent_runs": []
  },
  "rhythm": {
    "last_3_days_summary": [],
    "state_shift": []
  },
  "open_loops": [
    {
      "topic": "string",
      "kind": "emotional|decision|practical",
      "source": "chat|vault|memory",
      "last_seen": "ISO-8601",
      "followup_due": true
    }
  ],
  "current_themes": [],
  "avoid_topics": [],
  "recent_proactive_messages": []
}
```

---

### E. Expand `scripts/kelly-state-check.py`
**Priority:** High

#### Keep current sections
- Physical
- Schedule
- Focus

#### Add new sections
- Rhythm (last 2-3 days)
- Current themes
- Open loops
- Follow-up candidates
- Avoid / repetitive topics

#### Data sources to use
- recent daily notes from `/data/kelly-vault/01-Daily/2026/`
- `MEMORY.md`
- maybe `memory/*.md`
- existing context scripts

#### Important change
Replace `get_focus_state()` hardcoded string with actual context synthesis.
Right now it returns:
- `Kelly is currently focused on improving Shelly's architecture and context awareness.`

That should be dynamic, not hardcoded.

---

### F. Update `scripts/update-kelly-state.py`
**Priority:** High

Make it publish both:
- `kelly-state.md` for human-readable working memory
- active context JSON/MD for deeper system use

#### Add freshness metadata
Track:
- when body data updated
- when vault context updated
- when open loops were refreshed

This will help determine whether a proactive message is grounded enough.

---

## Phase 3 — Add proactive intelligence instead of literal prompts

### G. Add proactive message modes
**Priority:** High

Create a small module or helper functions for five message types:
- `pattern_notice`
- `body_read`
- `emotional_followup`
- `practical_assist`
- `identity_reinforcement`

This can live in:
- new file: `/data/workspace/scripts/proactive_message_modes.py`

or initially inside:
- `combined-context-check.py`

#### Contract
Each mode should take structured context and generate a message only if it has substance.

---

### H. Add follow-up tracking
**Priority:** High

Create a follow-up queue or list from recent conversation and vault notes.

Possible file:
- `/data/workspace/memory/kelly-followups.json`

#### Fields
- topic
- why it matters
- when noticed
- follow-up window
- resolved / unresolved
- last surfaced

#### Use
If a follow-up is due and still unresolved, it becomes a valid proactive trigger.

---

## Phase 4 — Evaluate quality over time

### I. Add proactive review logging
**Priority:** Medium

For each proactive message actually sent, log:
- timestamp
- type
- source signals
- why it passed gate
- whether topic was repetitive

Possible file:
- `/data/workspace/memory/proactive-message-log.jsonl`

This creates a review trail for weekly tuning.

---

### J. Add weekly scorecard script or manual review doc
**Priority:** Medium

Metrics:
- proactive messages sent
- proactive messages suppressed by gate
- repeats avoided
- follow-ups completed
- ratio of first-contact-by-Shelly vs first-contact-by-Kelly

---

## Concrete edits to make first

### Immediate code edits
1. `scripts/combined-context-check.py`
   - remove Starbucks branch
   - remove generic no-run branch
   - remove generic work prompt branch
   - add quality gate helper
   - make silence the default

2. `HEARTBEAT.md`
   - tighten proactive send criteria
   - explicitly ban literal filler prompts

3. `scripts/ai-message-wrapper.py`
   - add proactive message validator
   - block weak proactive sends

### Next edits
4. `scripts/kelly-state-check.py`
   - add rhythm / themes / open loops / avoid topics
   - remove hardcoded focus assumptions

5. `scripts/update-kelly-state.py`
   - emit richer Kelly State + active context

6. new context files
   - `memory/active-kelly-context.json`
   - `memory/kelly-followups.json`

---

## Definition of done
This system is improved when:
- heartbeat mostly updates awareness, not output
- proactive messages contain actual thought
- coffee/generic opener behavior is gone
- Shelly can follow up on real things without Kelly re-explaining them
- Shelly sometimes initiates with useful, non-literal presence

## Recommended order of execution
1. tighten heartbeat rules
2. patch `combined-context-check.py`
3. add message quality gate
4. build active context layer
5. add follow-up tracking
6. review for a few days and tune

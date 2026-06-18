---
name: shelly-evals
description: "Build, inspect, and run Shelly's evaluation set for proactive support, context awareness, interpretation quality, tone calibration, and memory/learning. Use when creating new Shelly eval cases, reviewing the v1 eval set, exporting structured eval data, generating scorecards, or scaffolding a repeatable eval workflow for Kelly's personal assistant behavior."
metadata: { "openclaw": { "emoji": "🧪", "requires": { "bins": ["python3"] } } }
---

# Shelly Evals

Use this skill to inspect Shelly's eval set, turn the spec into runnable cases, and score behavior changes against the same standard over time.

## Quick start

```bash
python3 scripts/shelly_evals.py list
python3 scripts/shelly_evals.py show EVAL-01
python3 scripts/shelly_evals.py prompt EVAL-01
python3 scripts/shelly_evals.py scorecard EVAL-01
python3 scripts/shelly_evals.py init-run baseline-v1
python3 scripts/shelly_evals.py validate-run assets/runs/<run-file>.json
python3 scripts/shelly_evals.py summarize-run assets/runs/<run-file>.json
python3 scripts/shelly_evals.py json
python3 scripts/shelly_evals.py jsonl
```

## What lives where

- Structured eval set: `assets/evals-v1.json`
- Scoring guide: `references/scoring.md`
- CLI helper: `scripts/shelly_evals.py`

If you need the narrative product doc, the source project note is:
- `/data/kelly-vault/02-Projects/Shelly Eval Spec v1.md`

## Workflow

### 1. Inspect the current eval set

Start by listing or showing the cases:

```bash
python3 scripts/shelly_evals.py list
python3 scripts/shelly_evals.py show EVAL-03
```

### 2. Generate a clean eval packet

Render a single-case packet for a fresh session or manual harness:

```bash
python3 scripts/shelly_evals.py prompt EVAL-03
```

Use this when you want a compact context + trigger block without the rest of the dataset.

### 3. Score a response

Create a blank scorecard template:

```bash
python3 scripts/shelly_evals.py scorecard EVAL-03
```

Then fill in:
- 1–5 scores for context, interpretation, recommendation, tone, restraint, and memory
- binary checks for contradiction, hallucination, noise, and better-than-silence
- fail tags and notes

Read `references/scoring.md` before scoring if you need the rubric.

### 4. Create and manage run files

Create a blank run file for the whole dataset:

```bash
python3 scripts/shelly_evals.py init-run baseline-v1
```

Validate a completed run file:

```bash
python3 scripts/shelly_evals.py validate-run assets/runs/<run-file>.json
```

Summarize a completed run file:

```bash
python3 scripts/shelly_evals.py summarize-run assets/runs/<run-file>.json
```

Run files live under `assets/runs/`.

### 5. Export structured data

Use JSON when another tool wants the full set:

```bash
python3 scripts/shelly_evals.py json
```

Use JSONL when building a runner or sending one row at a time into another system:

```bash
python3 scripts/shelly_evals.py jsonl
```

## How to use the evals well

- Prefer **10 strong cases** over a bloated benchmark.
- Keep cases grounded in real corrections Kelly has already made.
- If the same correction shows up 3 times, turn it into:
  - memory
  - a rule
  - an eval case
  - then a system behavior change
- When a proactive case is weak and not clearly better than silence, score it that way.
- Silence is a legitimate pass condition for some heartbeat / operational cases.

## Extending the dataset

When adding cases to `assets/evals-v1.json`, keep each case opinionated and specific.

Each case should include:
- `id`
- `title`
- `categories`
- `scenario`
- `context_packet`
- `trigger`
- `must_notice`
- `strong_response_qualities`
- `fail_conditions`
- `silence_expected`

Avoid vague cases like “be helpful.” Anchor each case to an actual recurring failure mode.

## When to read references

Read `references/scoring.md` when:
- you need scoring calibration
- you are comparing two responses
- you are deciding whether a proactive message was better than silence
- you are tagging recurring fail modes

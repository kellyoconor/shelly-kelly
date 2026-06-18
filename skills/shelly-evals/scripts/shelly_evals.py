#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import statistics
import sys
from datetime import datetime, timezone

SKILL_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = SKILL_DIR / "assets" / "evals-v1.json"
RESULTS_DIR = SKILL_DIR / "assets" / "runs"
SCORE_FIELDS = [
    "context_use",
    "interpretation",
    "recommendation",
    "tone_fit",
    "restraint",
    "memory_alignment",
]
BINARY_FIELDS = ["contradiction", "hallucination", "noise", "better_than_silence"]


def load_data():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def by_id(data, eval_id: str):
    for case in data["cases"]:
        if case["id"] == eval_id:
            return case
    raise SystemExit(f"Unknown eval id: {eval_id}")


def print_case(case):
    print(f"{case['id']} — {case['title']}")
    print(f"Categories: {', '.join(case['categories'])}")
    print(f"Silence expected: {'yes' if case['silence_expected'] else 'no'}")
    print()
    print("Scenario:")
    print(case["scenario"])
    print()
    print("Context packet:")
    for item in case["context_packet"]:
        print(f"- {item}")
    print()
    print("Trigger:")
    print(case["trigger"])
    print()
    print("Must notice:")
    for item in case["must_notice"]:
        print(f"- {item}")
    print()
    print("Strong response qualities:")
    for item in case["strong_response_qualities"]:
        print(f"- {item}")
    print()
    print("Fail conditions:")
    for item in case["fail_conditions"]:
        print(f"- {item}")


def list_cases(data):
    for case in data["cases"]:
        cats = ", ".join(case["categories"])
        print(f"{case['id']}\t{case['title']}\t[{cats}]")


def render_prompt(case):
    print("Use this packet in a fresh session or eval harness:")
    print()
    print("CONTEXT PACKET")
    for item in case["context_packet"]:
        print(f"- {item}")
    print()
    print("TRIGGER")
    print(case["trigger"])
    print()
    print("SCORING REMINDERS")
    print("- Must notice:")
    for item in case["must_notice"]:
        print(f"  - {item}")
    print("- Fail if:")
    for item in case["fail_conditions"]:
        print(f"  - {item}")


def blank_score(data, eval_id: str):
    case = by_id(data, eval_id)
    scorecard = make_blank_result(case)
    print(json.dumps(scorecard, indent=2, ensure_ascii=False))


def make_blank_result(case):
    return {
        "eval_id": case["id"],
        "title": case["title"],
        "response": None,
        "scores": {key: None for key in SCORE_FIELDS},
        "binary_checks": {
            "contradiction": False,
            "hallucination": False,
            "noise": False,
            "better_than_silence": None,
        },
        "fail_tags": [],
        "notes": "",
        "overall": None,
    }


def export_jsonl(data):
    for case in data["cases"]:
        print(json.dumps(case, ensure_ascii=False))


def safe_slug(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in {"-", "_"}:
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    slug = "".join(out).strip("-")
    return slug or "run"


def init_run(data, label: str):
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"{stamp}-{safe_slug(label)}.json"
    payload = {
        "run_label": label,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset": data["name"],
        "dataset_version": data.get("version"),
        "results": [make_blank_result(case) for case in data["cases"]],
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(path)


def load_results(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def result_mean(values):
    nums = [v for v in values if isinstance(v, (int, float))]
    if not nums:
        return None
    return round(statistics.mean(nums), 2)


def summarize_run(payload):
    results = payload.get("results", [])
    total = len(results)
    hard_fail_count = 0
    fail_tag_counts = {}
    score_buckets = {field: [] for field in SCORE_FIELDS}
    overalls = []
    better_than_silence_false = 0

    for item in results:
        scores = item.get("scores", {})
        for field in SCORE_FIELDS:
            val = scores.get(field)
            if isinstance(val, (int, float)):
                score_buckets[field].append(val)
        overall = item.get("overall")
        if isinstance(overall, (int, float)):
            overalls.append(overall)
        checks = item.get("binary_checks", {})
        if checks.get("contradiction") or checks.get("hallucination") or checks.get("noise"):
            hard_fail_count += 1
        if checks.get("better_than_silence") is False:
            better_than_silence_false += 1
        for tag in item.get("fail_tags", []):
            fail_tag_counts[tag] = fail_tag_counts.get(tag, 0) + 1

    print(f"Run label: {payload.get('run_label')}")
    print(f"Dataset: {payload.get('dataset')} v{payload.get('dataset_version')}")
    print(f"Cases scored: {total}")
    print(f"Mean overall: {result_mean(overalls)}")
    print(f"Hard fails (contradiction/hallucination/noise): {hard_fail_count}")
    print(f"Not better than silence: {better_than_silence_false}")
    print()
    print("Average scores:")
    for field in SCORE_FIELDS:
        print(f"- {field}: {result_mean(score_buckets[field])}")
    print()
    print("Top fail tags:")
    for tag, count in sorted(fail_tag_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
        print(f"- {tag}: {count}")


def validate_run(payload, data):
    case_ids = {case["id"] for case in data["cases"]}
    seen = set()
    errors = []
    for item in payload.get("results", []):
        eval_id = item.get("eval_id")
        if eval_id not in case_ids:
            errors.append(f"Unknown eval id in results: {eval_id}")
        if eval_id in seen:
            errors.append(f"Duplicate eval id in results: {eval_id}")
        seen.add(eval_id)
        for field in SCORE_FIELDS:
            if field not in item.get("scores", {}):
                errors.append(f"Missing score field {field} for {eval_id}")
        for field in BINARY_FIELDS:
            if field not in item.get("binary_checks", {}):
                errors.append(f"Missing binary field {field} for {eval_id}")
    missing = sorted(case_ids - seen)
    for eval_id in missing:
        errors.append(f"Missing eval result: {eval_id}")
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        raise SystemExit(1)
    print("Run file is valid")


def main():
    parser = argparse.ArgumentParser(description="Work with Shelly eval cases.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List eval ids and titles")

    show = sub.add_parser("show", help="Show a full eval case")
    show.add_argument("eval_id")

    prompt = sub.add_parser("prompt", help="Render a clean eval packet for a single case")
    prompt.add_argument("eval_id")

    score = sub.add_parser("scorecard", help="Print a blank JSON scorecard for a case")
    score.add_argument("eval_id")

    sub.add_parser("json", help="Print the full eval dataset as formatted JSON")
    sub.add_parser("jsonl", help="Print one eval case per JSONL row")

    init = sub.add_parser("init-run", help="Create a blank run file for all eval cases")
    init.add_argument("label")

    validate = sub.add_parser("validate-run", help="Validate a run file")
    validate.add_argument("path")

    summarize = sub.add_parser("summarize-run", help="Summarize a completed run file")
    summarize.add_argument("path")

    args = parser.parse_args()
    data = load_data()

    if args.cmd == "list":
        list_cases(data)
    elif args.cmd == "show":
        print_case(by_id(data, args.eval_id))
    elif args.cmd == "prompt":
        render_prompt(by_id(data, args.eval_id))
    elif args.cmd == "scorecard":
        blank_score(data, args.eval_id)
    elif args.cmd == "json":
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.cmd == "jsonl":
        export_jsonl(data)
    elif args.cmd == "init-run":
        init_run(data, args.label)
    elif args.cmd == "validate-run":
        validate_run(load_results(Path(args.path)), data)
    elif args.cmd == "summarize-run":
        summarize_run(load_results(Path(args.path)))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""The Mirror: reflective morning question generator."""

import json
import os
import subprocess
import sys
import random
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
TRENDS_FILE = DATA_DIR / "trends.json"
WORKSPACE = SKILL_DIR.parent.parent  # /data/workspace

OURA_SCRIPT = WORKSPACE / "skills" / "oura" / "scripts" / "oura.py"
STRAVA_SCRIPT = WORKSPACE / "skills" / "strava" / "scripts" / "strava.py"
CALENDAR_SCRIPT = WORKSPACE / "skills" / "google-calendar" / "scripts" / "calendar.py"

TODAY = datetime.now().strftime("%Y-%m-%d")
DOW = datetime.now().strftime("%A")  # Monday, Tuesday, etc.


def run_command(args, timeout=30):
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            cwd=str(WORKSPACE)
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


# ── Data Collection ─────────────────────────────────────────────

def get_oura_data():
    """Pull today's Oura brief summary."""
    raw = run_command(["python3", str(OURA_SCRIPT), "brief", TODAY])
    if not raw:
        raw = run_command(["python3", str(OURA_SCRIPT), "brief"])
    if not raw:
        return None

    data = {}
    for line in raw.split("\n"):
        line = line.strip()
        ll = line.lower()
        # Parse key metrics from brief output
        if "sleep score" in ll:
            data["sleep_score"] = _extract_number(line)
        elif "readiness" in ll and "score" in ll:
            data["readiness_score"] = _extract_number(line)
        elif "hrv" in ll:
            data["hrv"] = _extract_number(line)
        elif "lowest" in ll and "hr" in ll or "resting" in ll and "hr" in ll:
            data["resting_hr"] = _extract_number(line)
        elif "total sleep" in ll or "sleep duration" in ll:
            data["sleep_hours"] = _extract_number(line)
        elif "deep" in ll and ("min" in ll or "hr" in ll or "%" in ll):
            data["deep_sleep"] = _extract_number(line)
        elif "rem" in ll and ("min" in ll or "hr" in ll or "%" in ll):
            data["rem_sleep"] = _extract_number(line)
        elif "efficiency" in ll:
            data["sleep_efficiency"] = _extract_number(line)
        elif "temp" in ll:
            data["body_temp_deviation"] = _extract_number(line)

    data["_raw"] = raw
    return data if len(data) > 1 else None


def get_strava_data():
    """Pull recent Strava activities."""
    raw = run_command(["python3", str(STRAVA_SCRIPT), "runs", "5"])
    if not raw:
        raw = run_command(["python3", str(STRAVA_SCRIPT), "activities", "5"])
    if not raw:
        return None

    weekly_raw = run_command(["python3", str(STRAVA_SCRIPT), "weekly"])

    data = {
        "recent_activities_raw": raw,
        "weekly_raw": weekly_raw or "",
    }

    # Try to extract weekly mileage
    if weekly_raw:
        for line in weekly_raw.split("\n"):
            ll = line.lower()
            if "mile" in ll or "mi" in ll or "distance" in ll:
                n = _extract_number(line)
                if n and n > 0:
                    data["weekly_miles"] = n
                    break
            if "runs" in ll or "activities" in ll:
                n = _extract_number(line)
                if n and n > 0:
                    data["weekly_activity_count"] = int(n)

    # Count recent activities and check for today
    activity_count = 0
    has_today = False
    for line in raw.split("\n"):
        if any(c.isdigit() for c in line[:12] if c != ' '):
            activity_count += 1
            if TODAY in line:
                has_today = True
    data["recent_count"] = activity_count
    data["trained_today"] = has_today

    return data


def get_calendar_data():
    """Pull today's calendar events."""
    raw = run_command(["python3", str(CALENDAR_SCRIPT), "today"])
    if not raw:
        return None

    events = []
    for line in raw.split("\n"):
        line = line.strip()
        if line and not line.startswith("\n") and ":" in line and "No upcoming" not in line:
            if not line.endswith(":"):  # skip date headers
                events.append(line)

    return {
        "event_count": len(events),
        "events_raw": raw,
        "density": "heavy" if len(events) >= 5 else "moderate" if len(events) >= 3 else "light" if len(events) >= 1 else "clear",
    }


def _extract_number(text):
    """Extract the first number from a string."""
    import re
    match = re.search(r'[-+]?\d+\.?\d*', text)
    return float(match.group()) if match else None


# ── Snapshot Management ─────────────────────────────────────────

def save_snapshot(oura, strava, calendar):
    """Save today's data snapshot."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    snapshot = {
        "date": TODAY,
        "day_of_week": DOW,
        "oura": _clean_for_json(oura),
        "strava": _clean_for_json(strava),
        "calendar": _clean_for_json(calendar),
    }

    path = SNAPSHOTS_DIR / f"{TODAY}.json"
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)
    return snapshot


def _clean_for_json(data):
    """Remove raw text fields to keep snapshots compact."""
    if not data:
        return None
    cleaned = {k: v for k, v in data.items() if not k.endswith("_raw")}
    return cleaned if cleaned else None


def load_snapshots(days=60):
    """Load historical snapshots."""
    snapshots = []
    if not SNAPSHOTS_DIR.exists():
        return snapshots

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    for f in sorted(SNAPSHOTS_DIR.glob("*.json")):
        if f.stem >= cutoff:
            try:
                with open(f) as fh:
                    snapshots.append(json.load(fh))
            except (json.JSONDecodeError, IOError):
                continue
    return snapshots


# ── Trend Analysis ──────────────────────────────────────────────

def analyze_trends(snapshots, today_snapshot):
    """Analyze patterns across historical data."""
    trends = {
        "last_updated": TODAY,
        "day_count": len(snapshots),
        "weekly": [],
        "monthly": [],
        "observations": [],
    }

    oura_days = [s for s in snapshots if s.get("oura")]
    strava_days = [s for s in snapshots if s.get("strava")]

    # ── Weekly patterns (7+ days) ──
    if len(oura_days) >= 7:
        recent7 = oura_days[-7:]
        sleep_scores = [s["oura"].get("sleep_score") for s in recent7 if s["oura"].get("sleep_score")]
        hrvs = [s["oura"].get("hrv") for s in recent7 if s["oura"].get("hrv")]
        readiness = [s["oura"].get("readiness_score") for s in recent7 if s["oura"].get("readiness_score")]

        if sleep_scores:
            avg = sum(sleep_scores) / len(sleep_scores)
            trend_dir = _trend_direction(sleep_scores)
            trends["weekly"].append({"metric": "sleep_score", "avg": round(avg, 1), "direction": trend_dir, "values": sleep_scores})

        if hrvs:
            avg = sum(hrvs) / len(hrvs)
            trend_dir = _trend_direction(hrvs)
            trends["weekly"].append({"metric": "hrv", "avg": round(avg, 1), "direction": trend_dir, "values": hrvs})

        if readiness:
            avg = sum(readiness) / len(readiness)
            trend_dir = _trend_direction(readiness)
            trends["weekly"].append({"metric": "readiness", "avg": round(avg, 1), "direction": trend_dir, "values": readiness})

        # Day-of-week patterns
        dow_scores = {}
        for s in oura_days:
            dow = s.get("day_of_week", "")
            score = s.get("oura", {}).get("sleep_score")
            if dow and score:
                dow_scores.setdefault(dow, []).append(score)

        for day, scores in dow_scores.items():
            if len(scores) >= 3:
                avg = sum(scores) / len(scores)
                overall_avg = sum(s["oura"]["sleep_score"] for s in oura_days if s["oura"].get("sleep_score")) / max(len([s for s in oura_days if s["oura"].get("sleep_score")]), 1)
                if abs(avg - overall_avg) > 5:
                    direction = "higher" if avg > overall_avg else "lower"
                    trends["observations"].append(f"Sleep scores tend to be {direction} on {day}s (avg {avg:.0f} vs overall {overall_avg:.0f})")

    # ── Monthly patterns (30+ days) ──
    if len(oura_days) >= 30:
        first_half = oura_days[:15]
        second_half = oura_days[-15:]

        for metric in ["sleep_score", "hrv", "readiness_score"]:
            vals1 = [s["oura"].get(metric) for s in first_half if s["oura"].get(metric)]
            vals2 = [s["oura"].get(metric) for s in second_half if s["oura"].get(metric)]
            if vals1 and vals2:
                avg1 = sum(vals1) / len(vals1)
                avg2 = sum(vals2) / len(vals2)
                if abs(avg2 - avg1) > 3:
                    direction = "improving" if avg2 > avg1 else "declining"
                    trends["monthly"].append({"metric": metric, "direction": direction, "early_avg": round(avg1, 1), "recent_avg": round(avg2, 1)})

    # ── Cross-reference: training + sleep ──
    if len(strava_days) >= 7 and len(oura_days) >= 7:
        # Check if heavy training days correlate with next-day sleep
        for i in range(1, len(snapshots)):
            prev = snapshots[i - 1]
            curr = snapshots[i]
            if prev.get("strava", {}) and curr.get("oura", {}):
                trained = prev.get("strava", {}).get("trained_today", False)
                sleep = curr.get("oura", {}).get("sleep_score")
                if trained and sleep:
                    pass  # Could track correlation over time

    # ── Calendar density patterns ──
    cal_days = [s for s in snapshots if s.get("calendar")]
    heavy_days = [s for s in cal_days if s["calendar"].get("density") == "heavy"]
    if len(heavy_days) >= 3 and len(cal_days) >= 7:
        trends["observations"].append(f"{len(heavy_days)} heavy calendar days in the last {len(cal_days)} days tracked")

    # Save trends
    with open(TRENDS_FILE, "w") as f:
        json.dump(trends, f, indent=2)

    return trends


def _trend_direction(values):
    """Simple trend: compare first half avg to second half avg."""
    if len(values) < 4:
        return "stable"
    mid = len(values) // 2
    first = sum(values[:mid]) / mid
    second = sum(values[mid:]) / (len(values) - mid)
    diff = second - first
    if diff > 3:
        return "rising"
    elif diff < -3:
        return "falling"
    return "stable"


# ── Question Generation ────────────────────────────────────────

def generate_question(today_snapshot, snapshots, trends):
    """Generate ONE reflective question based on data signals."""
    candidates = []
    oura = today_snapshot.get("oura") or {}
    strava = today_snapshot.get("strava") or {}
    calendar = today_snapshot.get("calendar") or {}

    sleep_score = oura.get("sleep_score")
    readiness = oura.get("readiness_score")
    hrv = oura.get("hrv")
    resting_hr = oura.get("resting_hr")
    density = calendar.get("density", "unknown")
    weekly_miles = strava.get("weekly_miles")
    trained = strava.get("trained_today", False)

    # ── Day-level signals ──

    # Low sleep + heavy calendar
    if sleep_score and sleep_score < 70 and density == "heavy":
        candidates.append("You didn't sleep well, and today is packed. What's the story you're telling yourself about how today has to go?")

    # High readiness + light calendar
    if readiness and readiness > 85 and density in ("light", "clear"):
        candidates.append("Your body is ready and your calendar is open. What would you do today if nobody was watching?")

    # Low readiness
    if readiness and readiness < 65:
        candidates.append("Your body is asking for something today. If it could talk, what would it say?")

    # High HRV
    if hrv and hrv > 60:
        candidates.append("You're in a resilient state right now. What's one thing you've been avoiding that you could face today?")

    # Low HRV
    if hrv and hrv < 30:
        candidates.append("Your nervous system is running tight. What's sitting in the background that hasn't been named yet?")

    # Great sleep
    if sleep_score and sleep_score > 85:
        candidates.append("You slept deeply last night. What did you let go of before bed that you usually hold onto?")

    # Heavy calendar day
    if density == "heavy":
        candidates.append("Your day is full of other people's needs. Where do you show up in your own schedule?")

    # Clear calendar
    if density == "clear":
        candidates.append("Nothing on the calendar today. Does that feel like freedom or does it feel like something's missing?")

    # Training + low sleep
    if trained and sleep_score and sleep_score < 70:
        candidates.append("You're pushing through on low sleep. What's driving that — discipline or something else?")

    # ── Day-of-week signals ──

    if DOW == "Monday":
        candidates.append("It's Monday. What's one thing you want this week to be about that last week wasn't?")
        if readiness and readiness > 75:
            candidates.append("You're starting the week strong. What would it look like to protect that energy instead of spending it all by Wednesday?")

    if DOW == "Friday":
        candidates.append("The week is almost done. What surprised you about yourself this week?")

    if DOW in ("Saturday", "Sunday"):
        candidates.append("It's the weekend. What part of your weekday self are you relieved to set down?")

    # ── Weekly trend signals (7+ days) ──

    weekly_trends = trends.get("weekly", [])
    for wt in weekly_trends:
        metric = wt.get("metric")
        direction = wt.get("direction")

        if metric == "sleep_score" and direction == "falling":
            candidates.append("Your sleep has been slipping all week. What changed — or what hasn't changed that needs to?")
        elif metric == "sleep_score" and direction == "rising":
            candidates.append("Your sleep has been getting better each night. What's different about how you're ending your days?")

        if metric == "hrv" and direction == "falling":
            candidates.append("Your HRV has been trending down. What's accumulating — training, stress, or something harder to name?")
        elif metric == "hrv" and direction == "rising":
            candidates.append("Your HRV is climbing. Something is working. Do you know what it is, or is it happening without you noticing?")

        if metric == "readiness" and direction == "falling":
            candidates.append("Your readiness has been declining. If this week were a sentence, how would it end?")

    # ── Observation-based signals ──
    for obs in trends.get("observations", []):
        if "Sunday" in obs and "lower" in obs:
            candidates.append("Your body tenses up before the week starts. What does your body know about Mondays that you haven't said out loud?")
        if "heavy calendar" in obs.lower():
            candidates.append("Your schedule has been dense lately. When did you last have a day that was truly yours?")

    # ── Monthly trend signals (30+ days) ──
    for mt in trends.get("monthly", []):
        metric = mt.get("metric")
        direction = mt.get("direction")
        if metric == "sleep_score" and direction == "declining":
            candidates.append("Over the past month, your sleep has been quietly declining. What shifted in your life a month ago?")
        if metric == "hrv" and direction == "improving":
            candidates.append("Your HRV has been steadily improving over the past month. What are you doing right that you haven't given yourself credit for?")

    # ── Cross-reference signals ──

    # High training + declining readiness
    if weekly_miles and weekly_miles > 20 and readiness and readiness < 70:
        candidates.append("You've been putting in the miles, but your body isn't bouncing back. What are you running toward — or away from?")

    # Great sleep + low readiness (stress signal)
    if sleep_score and sleep_score > 80 and readiness and readiness < 65:
        candidates.append("You slept well but your body still feels depleted. What kind of tired is this — the kind sleep can fix, or the other kind?")

    # ── Fallbacks ──
    if not candidates:
        candidates = [
            "What's one thing you're carrying today that isn't yours to carry?",
            "If today had a theme, what would it be?",
            "What would you tell yourself six months from now about this moment?",
            "What are you pretending isn't bothering you?",
            "When was the last time you did something just because it felt good?",
        ]

    # Pick one — use date as seed for reproducibility
    seed = int(TODAY.replace("-", ""))
    random.seed(seed)
    return random.choice(candidates)


# ── Main ────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--trends" in args:
        if TRENDS_FILE.exists():
            with open(TRENDS_FILE) as f:
                trends = json.load(f)
            print(json.dumps(trends, indent=2))
        else:
            print("No trends data yet. Run mirror.py first to collect data.")
        return

    # Collect data
    oura = get_oura_data()
    strava = get_strava_data()
    calendar = get_calendar_data()

    # Save snapshot
    snapshot = save_snapshot(oura, strava, calendar)

    if "--snapshot-only" in args:
        print(f"Snapshot saved: {SNAPSHOTS_DIR / (TODAY + '.json')}")
        return

    # Load history
    snapshots = load_snapshots()

    # Analyze trends
    trends = analyze_trends(snapshots, snapshot)

    # Generate question
    question = generate_question(snapshot, snapshots, trends)
    print(question)


if __name__ == "__main__":
    main()

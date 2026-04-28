#!/usr/bin/env python3
"""
Generate Kelly's morning briefing text and optionally append a note to today's daily note.

Usage:
  python3 scripts/morning-briefing.py
  python3 scripts/morning-briefing.py --append-daily-note
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
WORKSPACE = Path("/data/workspace")
VAULT = Path("/data/kelly-vault")
PACKAGES_PATH = WORKSPACE / "skills/package-tracker/data/packages.json"
OURA_CMD = ["python3", "/data/workspace/skills/oura/scripts/oura.py", "brief"]
MIRROR_CMD = ["python3", "/data/workspace/skills/mirror/scripts/mirror.py"]
WEATHER_URL = "https://wttr.in/Philadelphia?format=Philadelphia:+%c+%t+Feels+like+%f"


@dataclass
class BriefData:
    weather: str | None = None
    oura: str | None = None
    mirror: str | None = None
    packages: str | None = None


def run_command(cmd: list[str], timeout: int = 20) -> str | None:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    text = (result.stdout or "").strip()
    return text or None


def fetch_weather() -> str | None:
    return run_command(["curl", "-sS", WEATHER_URL], timeout=15)


def fetch_oura() -> str | None:
    text = run_command(OURA_CMD, timeout=25)
    if not text:
        return None
    try:
        data = json.loads(text)
    except Exception:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return " ".join(lines[:3]) if lines else text

    sleep_score = ((data.get("sleep") or {}).get("score"))
    readiness_score = ((data.get("readiness") or {}).get("score"))
    bits = []
    if readiness_score is not None:
        bits.append(f"readiness {readiness_score}%")
    if sleep_score is not None:
        bits.append(f"sleep {sleep_score}%")
    return ", ".join(bits) if bits else None


def fetch_mirror() -> str | None:
    text = run_command(MIRROR_CMD, timeout=25)
    if not text:
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    # Prefer the last non-empty line in case the script prints setup/context first.
    return lines[-1]


def summarize_packages() -> str | None:
    if not PACKAGES_PATH.exists():
        return None
    try:
        data = json.loads(PACKAGES_PATH.read_text())
    except Exception:
        return None
    if not isinstance(data, list):
        return None

    active = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if item.get("delivered"):
            continue
        status = (item.get("status") or "unknown").replace("_", " ")
        name = item.get("name") or item.get("carrier") or "package"
        active.append(f"{name} ({status})")

    if not active:
        return None
    if len(active) == 1:
        return f"Package watch: {active[0]}."
    return f"Package watch: {len(active)} active — " + "; ".join(active[:3]) + ("." if len(active) <= 3 else "; more in tracker.")


def build_brief(data: BriefData) -> str:
    parts: list[str] = []
    if data.weather:
        parts.append(f"Morning ☀️ {data.weather}.")
    else:
        parts.append("Morning ☀️")

    if data.oura:
        parts.append(f"Oura: {data.oura}")
    if data.packages:
        parts.append(data.packages)
    if data.mirror:
        parts.append(f"Mirror: {data.mirror}")

    return "\n".join(parts)


def daily_note_path(now: datetime) -> Path:
    return VAULT / f"01-Daily/{now.year}/{now.strftime('%Y-%m-%d')}.md"


def ensure_daily_note(path: Path, now: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(
        f"# {now.strftime('%B %d, %Y')}\n\n"
        "## Weather\n- \n\n"
        "## Events\n- \n\n"
        "## Health\n- \n\n"
        "## Thoughts\n- \n\n"
        "## Tasks\n- \n\n"
        "## Notes\n- \n"
    )


def insert_under_section(content: str, section: str, bullet: str, path: Path) -> None:
    lines = path.read_text().splitlines(keepends=True)
    header = f"## {section}"
    insert_index = len(lines)
    found = False
    for i, line in enumerate(lines):
        if line.strip() == header:
            found = True
            insert_index = i + 1
            while insert_index < len(lines) and not lines[insert_index].startswith("## "):
                insert_index += 1
            break
    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.extend([f"\n{header}\n"])
        insert_index = len(lines)
    lines.insert(insert_index, bullet + "\n")
    path.write_text("".join(lines))


def append_daily_note(data: BriefData) -> None:
    now = datetime.now(ET)
    path = daily_note_path(now)
    ensure_daily_note(path, now)
    stamp = now.strftime("%I:%M %p").lstrip("0")
    if data.weather:
        insert_under_section("Weather", "Weather", f"- **{stamp}**: {data.weather}", path)
    if data.oura:
        insert_under_section("Health", "Health", f"- **{stamp}**: {data.oura}", path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--append-daily-note", action="store_true")
    args = parser.parse_args()

    data = BriefData(
        weather=fetch_weather(),
        oura=fetch_oura(),
        mirror=fetch_mirror(),
        packages=summarize_packages(),
    )

    brief = build_brief(data)
    print(brief)

    if args.append_daily_note:
        append_daily_note(data)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

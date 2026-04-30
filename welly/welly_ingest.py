#!/usr/bin/env python3
"""
welly-ingest: Data collection for Kelly's body-awareness companion

Pulls Oura summary, Strava activity, 7-day trends, and manual notes
to feed into Welly's interpretation system.
"""

import importlib.util
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class WellyIngest:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        self.skills_path = self.workspace / "skills"
        self.memory_path = self.workspace / "memory"

    def setup_database(self):
        """Initialize Welly's memory database if it doesn't exist"""
        self.db_path.parent.mkdir(exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS daily_state (
                date TEXT PRIMARY KEY,
                sleep_quality INTEGER,
                readiness INTEGER,
                hrv_rmssd REAL,
                resting_hr INTEGER,
                workout_load REAL,
                soreness INTEGER,
                energy INTEGER,
                motivation INTEGER,
                stress INTEGER,
                mood INTEGER,
                feel_like_self TEXT,
                notes TEXT,
                created_at TEXT
            )
            '''
        )

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS oura_data (
                date TEXT PRIMARY KEY,
                sleep_data TEXT,
                readiness_data TEXT,
                activity_data TEXT,
                heartrate_data TEXT,
                retrieved_at TEXT
            )
            '''
        )

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS strava_data (
                date TEXT PRIMARY KEY,
                runs_data TEXT,
                weekly_data TEXT,
                retrieved_at TEXT
            )
            '''
        )

        conn.commit()
        conn.close()

    def ingest_oura_data(self, date_str: Optional[str] = None) -> Dict:
        """Pull Oura data using existing skill"""
        if not date_str:
            date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        oura_script = self.skills_path / "oura" / "scripts" / "oura.py"
        if not oura_script.exists():
            return {"error": "Oura skill not found"}

        try:
            result = subprocess.run(
                ["python3", str(oura_script), "brief", date_str],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )

            if result.returncode != 0:
                return {"error": f"Oura API error: {result.stderr}"}

            brief_data = self._parse_oura_output(result.stdout)
            self._cache_oura_data(date_str, brief_data)
            self._upsert_daily_state_objective(date_str, oura_data=brief_data)
            return brief_data

        except Exception as e:
            return {"error": f"Failed to fetch Oura data: {str(e)}"}

    def ingest_strava_data(self, date_str: Optional[str] = None) -> Dict:
        """Pull Strava data using existing skill"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        strava_script = self.skills_path / "strava" / "scripts" / "strava.py"
        if not strava_script.exists():
            return {"error": "Strava skill not found"}

        try:
            runs_result = subprocess.run(
                ["python3", str(strava_script), "runs", "7"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )
            weekly_result = subprocess.run(
                ["python3", str(strava_script), "weekly"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )

            if runs_result.returncode != 0 or weekly_result.returncode != 0:
                return {"error": "Strava API error"}

            strava_data = {
                "runs": self._parse_strava_runs(runs_result.stdout),
                "weekly": self._parse_strava_weekly(weekly_result.stdout),
            }

            self._cache_strava_data(date_str, strava_data)
            self._upsert_daily_state_objective(date_str, strava_data=strava_data)
            for run in strava_data.get("runs", []):
                run_date = run.get("_date") or run.get("date")
                if run_date:
                    self._upsert_daily_state_objective(run_date, strava_data=strava_data)

            return strava_data

        except Exception as e:
            return {"error": f"Failed to fetch Strava data: {str(e)}"}

    def ingest_manual_checkin(
        self,
        energy: int,
        soreness: int,
        stress: int,
        mood: int,
        feel_like_self: str,
        notes: str = "",
    ) -> Dict:
        """Store manual check-in data without overwriting objective fields."""
        date_str = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM daily_state WHERE date = ?', (date_str,))
            existing = cursor.fetchone()

            sleep_quality = existing[1] if existing else None
            readiness = existing[2] if existing else None
            hrv_rmssd = existing[3] if existing else None
            resting_hr = existing[4] if existing else None
            workout_load = existing[5] if existing else None
            created_at = (existing[13] if existing and existing[13] else datetime.now().isoformat())

            cursor.execute(
                '''
                INSERT OR REPLACE INTO daily_state
                (date, sleep_quality, readiness, hrv_rmssd, resting_hr, workout_load,
                 soreness, energy, motivation, stress, mood, feel_like_self, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    date_str,
                    sleep_quality,
                    readiness,
                    hrv_rmssd,
                    resting_hr,
                    workout_load,
                    soreness,
                    energy,
                    None,
                    stress,
                    mood,
                    feel_like_self,
                    notes,
                    created_at,
                ),
            )

            conn.commit()
            return {"success": True, "date": date_str}

        except Exception as e:
            return {"error": f"Failed to store manual check-in: {str(e)}"}
        finally:
            conn.close()

    def get_7day_trends(self) -> Dict:
        """Get 7-day trends from stored data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''
                SELECT date, sleep_quality, readiness, energy, soreness, stress, mood, feel_like_self, workout_load
                FROM daily_state
                WHERE date >= ? AND date <= ?
                ORDER BY date
                ''',
                (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
            )

            daily_states = []
            for row in cursor.fetchall():
                daily_states.append(
                    {
                        "date": row[0],
                        "sleep_quality": row[1],
                        "readiness": row[2],
                        "energy": row[3],
                        "soreness": row[4],
                        "stress": row[5],
                        "mood": row[6],
                        "feel_like_self": row[7],
                        "workout_load": row[8],
                    }
                )

            cursor.execute(
                '''
                SELECT date, readiness_data, sleep_data
                FROM oura_data
                WHERE date >= ? AND date <= ?
                ORDER BY date
                ''',
                (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
            )

            oura_trends = []
            for row in cursor.fetchall():
                oura_trends.append(
                    {
                        "date": row[0],
                        "readiness_data": json.loads(row[1]) if row[1] else None,
                        "sleep_data": json.loads(row[2]) if row[2] else None,
                    }
                )

            return {
                "daily_states": daily_states,
                "oura_trends": oura_trends,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            }

        except Exception as e:
            return {"error": f"Failed to get trends: {str(e)}"}
        finally:
            conn.close()

    def get_memory_notes(self, days_back: int = 3) -> List[str]:
        """Get relevant notes from memory files"""
        notes = []

        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = self.memory_path / f"{date}.md"

            if memory_file.exists():
                with open(memory_file, 'r') as f:
                    content = f.read()
                    health_notes = self._extract_health_notes(content)
                    if health_notes:
                        notes.extend(health_notes)

        return notes

    def ingest_run_subjective_response(self, response_text: str) -> Dict:
        """Parse a natural-language run response and merge it into Welly memory."""
        try:
            parser_module = self._load_module(self.workspace / "welly" / "rpe_response_parser.py", "rpe_response_parser")
            tracker_module = self._load_module(self.workspace / "welly" / "rpe_tracker.py", "rpe_tracker")
        except Exception as e:
            return {"error": f"Could not load subjective capture modules: {e}"}

        run_data = self._get_recent_run()
        if not run_data:
            return {"error": "No recent run found to attach subjective response to"}

        parser = parser_module.RPEResponseParser()
        parsed = parser.parse_response(response_text, run_data)

        if parsed.get("confidence", 0) < 0.2:
            return {"logged": False, "reason": "Low confidence in parsing", "parsed": parsed}

        tracker = tracker_module.RPETracker(str(self.workspace))
        tracker.setup_rpe_tables()
        tracker.capture_post_run_rpe(
            run_data,
            parsed["perceived_effort"],
            parsed["leg_feeling"],
            parsed["satisfaction"],
            parsed["notes"],
        )

        date_str = run_data.get("_date") or datetime.now().strftime('%Y-%m-%d')
        subjective_fields = self._subjective_fields_from_run_response(parsed, response_text)
        self._upsert_daily_state_subjective(date_str, **subjective_fields)

        return {
            "logged": True,
            "date": date_str,
            "run_id": run_data.get("id"),
            "parsed": parsed,
            "daily_state_updates": subjective_fields,
            "summary": f"Logged run subjective data for {date_str}: effort {parsed['perceived_effort']}/10, legs {parsed['leg_feeling']}/10, satisfaction {parsed['satisfaction']}/10",
        }

    def backfill_recent_days(self, days: int = 7) -> Dict:
        """Backfill recent objective data into daily_state."""
        self.setup_database()
        results = {"days_requested": days, "dates": [], "errors": []}

        strava_data = self.ingest_strava_data(datetime.now().strftime('%Y-%m-%d'))
        if strava_data.get("error"):
            results["errors"].append(f"strava: {strava_data['error']}")
            strava_data = {}

        for i in range(days):
            date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            oura_data = self.ingest_oura_data(date_str)
            if oura_data.get("error"):
                results["errors"].append(f"oura {date_str}: {oura_data['error']}")
                oura_data = {}
            self._upsert_daily_state_objective(date_str, oura_data=oura_data, strava_data=strava_data)
            results["dates"].append(date_str)

        return results

    def _upsert_daily_state_subjective(
        self,
        date_str: str,
        energy: Optional[int] = None,
        soreness: Optional[int] = None,
        motivation: Optional[int] = None,
        stress: Optional[int] = None,
        mood: Optional[int] = None,
        feel_like_self: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        """Merge subjective fields into daily_state without clobbering objective metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM daily_state WHERE date = ?', (date_str,))
            existing = cursor.fetchone()

            current = {
                "sleep_quality": existing[1] if existing else None,
                "readiness": existing[2] if existing else None,
                "hrv_rmssd": existing[3] if existing else None,
                "resting_hr": existing[4] if existing else None,
                "workout_load": existing[5] if existing else None,
                "soreness": existing[6] if existing else None,
                "energy": existing[7] if existing else None,
                "motivation": existing[8] if existing else None,
                "stress": existing[9] if existing else None,
                "mood": existing[10] if existing else None,
                "feel_like_self": existing[11] if existing else None,
                "notes": existing[12] if existing else None,
                "created_at": (existing[13] if existing and existing[13] else datetime.now().isoformat()),
            }

            updates = {
                "energy": energy,
                "soreness": soreness,
                "motivation": motivation,
                "stress": stress,
                "mood": mood,
                "feel_like_self": feel_like_self,
            }
            for key, value in updates.items():
                if value is not None:
                    current[key] = value

            if notes:
                current["notes"] = f"{current['notes']} | {notes}" if current.get("notes") else notes

            cursor.execute(
                '''
                INSERT OR REPLACE INTO daily_state
                (date, sleep_quality, readiness, hrv_rmssd, resting_hr, workout_load,
                 soreness, energy, motivation, stress, mood, feel_like_self, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    date_str,
                    current["sleep_quality"],
                    current["readiness"],
                    current["hrv_rmssd"],
                    current["resting_hr"],
                    current["workout_load"],
                    current["soreness"],
                    current["energy"],
                    current["motivation"],
                    current["stress"],
                    current["mood"],
                    current["feel_like_self"],
                    current["notes"],
                    current["created_at"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _upsert_daily_state_objective(
        self,
        date_str: str,
        oura_data: Optional[Dict] = None,
        strava_data: Optional[Dict] = None,
    ):
        """Merge objective Oura/Strava metrics into daily_state without clobbering manual fields."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM daily_state WHERE date = ?', (date_str,))
            existing = cursor.fetchone()

            current = {
                "sleep_quality": None,
                "readiness": None,
                "hrv_rmssd": None,
                "resting_hr": None,
                "workout_load": None,
                "soreness": None,
                "energy": None,
                "motivation": None,
                "stress": None,
                "mood": None,
                "feel_like_self": None,
                "notes": None,
                "created_at": datetime.now().isoformat(),
            }

            if existing:
                current.update(
                    {
                        "sleep_quality": existing[1],
                        "readiness": existing[2],
                        "hrv_rmssd": existing[3],
                        "resting_hr": existing[4],
                        "workout_load": existing[5],
                        "soreness": existing[6],
                        "energy": existing[7],
                        "motivation": existing[8],
                        "stress": existing[9],
                        "mood": existing[10],
                        "feel_like_self": existing[11],
                        "notes": existing[12],
                        "created_at": existing[13] or current["created_at"],
                    }
                )

            if oura_data:
                sleep = oura_data.get("sleep", {}) or {}
                readiness = oura_data.get("readiness", {}) or {}
                current["sleep_quality"] = sleep.get("score", current["sleep_quality"])
                current["readiness"] = readiness.get("score", current["readiness"])
                current["hrv_rmssd"] = readiness.get("hrv") or readiness.get("average_hrv") or current["hrv_rmssd"]
                current["resting_hr"] = readiness.get("resting_hr") or readiness.get("lowest_hr") or current["resting_hr"]

            if strava_data:
                runs = strava_data.get("runs", []) or []
                run_for_day = None
                for run in runs:
                    run_date = run.get("_date") or run.get("date")
                    if run_date == date_str:
                        run_for_day = run
                        break

                if run_for_day:
                    workout_load = run_for_day.get("suffer_score")
                    if workout_load is None:
                        miles = run_for_day.get("_distance_mi") or run_for_day.get("miles") or 0
                        hr = run_for_day.get("average_heartrate") or run_for_day.get("hr_avg") or 0
                        workout_load = round(float(miles) * (float(hr) / 10.0), 1) if miles and hr else float(miles)
                    current["workout_load"] = workout_load

            cursor.execute(
                '''
                INSERT OR REPLACE INTO daily_state
                (date, sleep_quality, readiness, hrv_rmssd, resting_hr, workout_load,
                 soreness, energy, motivation, stress, mood, feel_like_self, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    date_str,
                    current["sleep_quality"],
                    current["readiness"],
                    current["hrv_rmssd"],
                    current["resting_hr"],
                    current["workout_load"],
                    current["soreness"],
                    current["energy"],
                    current["motivation"],
                    current["stress"],
                    current["mood"],
                    current["feel_like_self"],
                    current["notes"],
                    current["created_at"],
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _load_module(self, path: Path, module_name: str):
        module_dir = str(path.parent)
        if module_dir not in sys.path:
            sys.path.insert(0, module_dir)
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _get_recent_run(self) -> Optional[Dict]:
        try:
            result = subprocess.run(
                ["python3", str(self.skills_path / "strava" / "scripts" / "strava.py"), "runs", "1"],
                capture_output=True,
                text=True,
                cwd=self.workspace,
            )
            if result.returncode != 0:
                return None
            runs = json.loads(result.stdout)
            if not runs:
                return None
            today = datetime.now().strftime('%Y-%m-%d')
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
            return runs[0] if runs[0].get("_date") in [today, yesterday] else None
        except Exception:
            return None

    def _ten_to_five(self, value: Optional[int], invert: bool = False) -> Optional[int]:
        if value is None:
            return None
        base = max(1, min(10, int(round(value))))
        if invert:
            base = 11 - base
        return max(1, min(5, int(round(base / 2))))

    def _subjective_fields_from_run_response(self, parsed: Dict, response_text: str) -> Dict:
        effort = parsed.get("perceived_effort")
        legs = parsed.get("leg_feeling")
        satisfaction = parsed.get("satisfaction")
        text = response_text.lower()

        stress = 4 if any(word in text for word in ["stressed", "stress", "anxious", "overwhelmed"]) else None
        if stress is None and any(word in text for word in ["period", "cramps", "pms"]):
            stress = 3

        feel_like_self = None
        if satisfaction is not None and satisfaction >= 7 and legs is not None and legs >= 6:
            feel_like_self = "yes"
        elif satisfaction is not None and satisfaction <= 4:
            feel_like_self = "no"
        elif effort is not None or legs is not None:
            feel_like_self = "somewhat"

        notes = f"Auto subjective capture from run response: {response_text.strip()}"

        return {
            "energy": self._ten_to_five(effort, invert=True),
            "soreness": self._ten_to_five(legs, invert=True),
            "motivation": self._ten_to_five(satisfaction),
            "stress": stress,
            "mood": self._ten_to_five(satisfaction),
            "feel_like_self": feel_like_self,
            "notes": notes,
        }

    def _parse_oura_output(self, output: str) -> Dict:
        """Parse Oura script output into structured data."""
        try:
            data = json.loads(output)
            return data if isinstance(data, dict) else {"sleep": {}, "readiness": {}, "activity": {}, "heartrate": {}}
        except Exception:
            return {"sleep": {}, "readiness": {}, "activity": {}, "heartrate": {}}

    def _parse_strava_runs(self, output: str) -> List[Dict]:
        """Parse Strava runs output."""
        try:
            data = json.loads(output)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _parse_strava_weekly(self, output: str) -> Dict:
        """Parse Strava weekly summary."""
        try:
            data = json.loads(output)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _cache_oura_data(self, date_str: str, data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''
                INSERT OR REPLACE INTO oura_data
                (date, sleep_data, readiness_data, activity_data, heartrate_data, retrieved_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    date_str,
                    json.dumps(data.get("sleep", {})),
                    json.dumps(data.get("readiness", {})),
                    json.dumps(data.get("activity", {})),
                    json.dumps(data.get("heartrate", {})),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _cache_strava_data(self, date_str: str, data: Dict):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                '''
                INSERT OR REPLACE INTO strava_data
                (date, runs_data, weekly_data, retrieved_at)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    date_str,
                    json.dumps(data.get("runs", [])),
                    json.dumps(data.get("weekly", {})),
                    datetime.now().isoformat(),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def _extract_health_notes(self, content: str) -> List[str]:
        health_keywords = [
            "tired", "energy", "sore", "pain", "sleep", "recovery", "run",
            "workout", "training", "rest", "stress", "mood", "feeling",
        ]

        lines = content.split('\n')
        health_notes = []
        for line in lines:
            if any(keyword in line.lower() for keyword in health_keywords):
                clean_line = line.strip()
                if len(clean_line) > 10:
                    health_notes.append(clean_line)
        return health_notes


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly_ingest.py setup           # Initialize database")
        print("  python3 welly_ingest.py oura [date]     # Pull Oura data")
        print("  python3 welly_ingest.py strava [date]   # Pull Strava data")
        print("  python3 welly_ingest.py checkin         # Manual check-in")
        print("  python3 welly_ingest.py trends          # Get 7-day trends")
        print("  python3 welly_ingest.py backfill [days] # Backfill recent objective data")
        print("  python3 welly_ingest.py subjective-run <text> # Parse a natural run response")
        return

    ingest = WellyIngest()
    command = sys.argv[1]

    if command == "setup":
        ingest.setup_database()
        print("✅ Welly database initialized")

    elif command == "oura":
        date_str = sys.argv[2] if len(sys.argv) > 2 else None
        result = ingest.ingest_oura_data(date_str)
        print(json.dumps(result, indent=2))

    elif command == "strava":
        date_str = sys.argv[2] if len(sys.argv) > 2 else None
        result = ingest.ingest_strava_data(date_str)
        print(json.dumps(result, indent=2))

    elif command == "checkin":
        print("Manual Check-in")
        energy = int(input("Energy (1-5): "))
        soreness = int(input("Soreness (1-5): "))
        stress = int(input("Stress (1-5): "))
        mood = int(input("Mood (1-5): "))
        feel_like_self = input("Do you feel like yourself today? (yes/somewhat/no): ")
        notes = input("Any notes: ")
        result = ingest.ingest_manual_checkin(energy, soreness, stress, mood, feel_like_self, notes)
        print(json.dumps(result, indent=2))

    elif command == "trends":
        result = ingest.get_7day_trends()
        print(json.dumps(result, indent=2))

    elif command == "backfill":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        result = ingest.backfill_recent_days(days)
        print(json.dumps(result, indent=2))

    elif command == "subjective-run":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Provide the natural-language run response text"}, indent=2))
            return
        response_text = " ".join(sys.argv[2:])
        result = ingest.ingest_run_subjective_response(response_text)
        print(json.dumps(result, indent=2))

    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()

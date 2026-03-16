#!/usr/bin/env python3
"""
welly-ingest: Data collection for Kelly's body-awareness companion

Pulls Oura summary, Strava activity, 7-day trends, and manual notes
to feed into Welly's interpretation system.
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
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
        
        # Daily state table
        cursor.execute('''
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
        ''')
        
        # Oura raw data cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oura_data (
                date TEXT PRIMARY KEY,
                sleep_data TEXT,
                readiness_data TEXT,
                activity_data TEXT,
                heartrate_data TEXT,
                retrieved_at TEXT
            )
        ''')
        
        # Strava raw data cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strava_data (
                date TEXT PRIMARY KEY,
                runs_data TEXT,
                weekly_data TEXT,
                retrieved_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def ingest_oura_data(self, date_str: Optional[str] = None) -> Dict:
        """Pull Oura data using existing skill"""
        if not date_str:
            # Default to yesterday for sleep data
            date_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        oura_script = self.skills_path / "oura" / "scripts" / "oura.py"
        if not oura_script.exists():
            return {"error": "Oura skill not found"}
        
        try:
            # Get brief summary (combined data)
            result = subprocess.run([
                "python3", str(oura_script), "brief", date_str
            ], capture_output=True, text=True, cwd=self.workspace)
            
            if result.returncode != 0:
                return {"error": f"Oura API error: {result.stderr}"}
            
            # Parse the output - Oura script returns structured data
            brief_data = self._parse_oura_output(result.stdout)
            
            # Store in cache
            self._cache_oura_data(date_str, brief_data)
            
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
            # Get recent runs
            runs_result = subprocess.run([
                "python3", str(strava_script), "runs", "7"
            ], capture_output=True, text=True, cwd=self.workspace)
            
            # Get weekly summary  
            weekly_result = subprocess.run([
                "python3", str(strava_script), "weekly"
            ], capture_output=True, text=True, cwd=self.workspace)
            
            if runs_result.returncode != 0 or weekly_result.returncode != 0:
                return {"error": "Strava API error"}
            
            strava_data = {
                "runs": self._parse_strava_runs(runs_result.stdout),
                "weekly": self._parse_strava_weekly(weekly_result.stdout)
            }
            
            # Store in cache
            self._cache_strava_data(date_str, strava_data)
            
            return strava_data
            
        except Exception as e:
            return {"error": f"Failed to fetch Strava data: {str(e)}"}
    
    def ingest_manual_checkin(self, energy: int, legs: int, stress: int, 
                             mood: int, feel_like_self: str, notes: str = "") -> Dict:
        """Store manual check-in data"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO daily_state 
                (date, energy, legs, stress, mood, feel_like_self, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, energy, legs, stress, mood, feel_like_self, notes,
                  datetime.now().isoformat()))
            
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
            # Get daily state trends
            cursor.execute('''
                SELECT date, sleep_quality, readiness, energy, legs, stress, mood, feel_like_self
                FROM daily_state 
                WHERE date >= ? AND date <= ?
                ORDER BY date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            daily_states = []
            for row in cursor.fetchall():
                daily_states.append({
                    "date": row[0],
                    "sleep_quality": row[1],
                    "readiness": row[2],
                    "energy": row[3],
                    "legs": row[4],
                    "stress": row[5],
                    "mood": row[6],
                    "feel_like_self": row[7]
                })
            
            # Get Oura trend data
            cursor.execute('''
                SELECT date, readiness_data, sleep_data
                FROM oura_data
                WHERE date >= ? AND date <= ?
                ORDER BY date
            ''', (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            
            oura_trends = []
            for row in cursor.fetchall():
                oura_trends.append({
                    "date": row[0],
                    "readiness_data": json.loads(row[1]) if row[1] else None,
                    "sleep_data": json.loads(row[2]) if row[2] else None
                })
            
            return {
                "daily_states": daily_states,
                "oura_trends": oura_trends,
                "period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
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
                    # Extract health/training related notes
                    health_notes = self._extract_health_notes(content)
                    if health_notes:
                        notes.extend(health_notes)
        
        return notes
    
    def _parse_oura_output(self, output: str) -> Dict:
        """Parse Oura script output into structured data"""
        # This would parse the actual Oura output format
        # For now, return a placeholder structure
        lines = output.strip().split('\n')
        
        parsed = {
            "sleep": {},
            "readiness": {},
            "activity": {},
            "heartrate": {}
        }
        
        # Would implement actual parsing based on Oura script output format
        return parsed
    
    def _parse_strava_runs(self, output: str) -> List[Dict]:
        """Parse Strava runs output"""
        # Would parse actual Strava runs format
        return []
    
    def _parse_strava_weekly(self, output: str) -> Dict:
        """Parse Strava weekly summary"""
        # Would parse actual Strava weekly format  
        return {}
    
    def _cache_oura_data(self, date_str: str, data: Dict):
        """Cache Oura data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO oura_data 
                (date, sleep_data, readiness_data, activity_data, heartrate_data, retrieved_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date_str, 
                  json.dumps(data.get("sleep", {})),
                  json.dumps(data.get("readiness", {})),
                  json.dumps(data.get("activity", {})),
                  json.dumps(data.get("heartrate", {})),
                  datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            print(f"Error caching Oura data: {e}")
        finally:
            conn.close()
    
    def _cache_strava_data(self, date_str: str, data: Dict):
        """Cache Strava data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO strava_data
                (date, runs_data, weekly_data, retrieved_at) 
                VALUES (?, ?, ?, ?)
            ''', (date_str,
                  json.dumps(data.get("runs", [])),
                  json.dumps(data.get("weekly", {})),
                  datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            print(f"Error caching Strava data: {e}")
        finally:
            conn.close()
    
    def _extract_health_notes(self, content: str) -> List[str]:
        """Extract health/training related notes from memory content"""
        health_keywords = [
            "tired", "energy", "sore", "pain", "sleep", "recovery", "run", 
            "workout", "training", "rest", "stress", "mood", "feeling"
        ]
        
        lines = content.split('\n')
        health_notes = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in health_keywords):
                # Clean up the line and add if it's substantial
                clean_line = line.strip()
                if len(clean_line) > 10:  # Avoid very short matches
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
        # Interactive manual check-in
        print("Manual Check-in")
        energy = int(input("Energy (1-5): "))
        legs = int(input("Legs (1-5): "))
        stress = int(input("Stress (1-5): "))
        mood = int(input("Mood (1-5): "))
        feel_like_self = input("Do you feel like yourself today? (yes/somewhat/no): ")
        notes = input("Any notes: ")
        
        result = ingest.ingest_manual_checkin(energy, legs, stress, mood, feel_like_self, notes)
        print(json.dumps(result, indent=2))
    
    elif command == "trends":
        result = ingest.get_7day_trends()
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
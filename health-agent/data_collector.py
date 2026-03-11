#!/usr/bin/env python3
"""
Data Collector for Kelly's Health Correlations Agent.
Pulls data from Oura and Strava skills and stores for analysis.
"""

import json
import subprocess
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import HealthConfig, OURA_SKILL_PATH, STRAVA_SKILL_PATH

class HealthDataCollector:
    """Collects and stores health data from Oura and Strava."""
    
    def __init__(self):
        self.data_path = HealthConfig.get_data_path()
        self.daily_data_file = HealthConfig.get_data_path("daily_data.json")
        self.historical_data = self._load_historical_data()
    
    def _load_historical_data(self) -> Dict:
        """Load existing historical data from storage."""
        if os.path.exists(self.daily_data_file):
            try:
                with open(self.daily_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load historical data: {e}")
        return {}
    
    def _save_historical_data(self):
        """Save historical data to storage."""
        try:
            with open(self.daily_data_file, 'w') as f:
                json.dump(self.historical_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving historical data: {e}")
    
    def _run_skill_command(self, skill_path: str, command: List[str]) -> Optional[Dict]:
        """Run a command in a skill directory and return JSON output."""
        try:
            result = subprocess.run(
                ["python3"] + command,
                cwd=skill_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0:
                print(f"Command failed in {skill_path}: {result.stderr}")
                return None
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Error running command in {skill_path}: {e}")
            return None
    
    def collect_oura_data(self, date: str = None) -> Optional[Dict]:
        """Collect Oura data for specified date (default: yesterday)."""
        if not date:
            # Default to yesterday for sleep data
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            date = yesterday
        
        # Get combined brief (sleep + readiness + activity)
        oura_data = self._run_skill_command(
            OURA_SKILL_PATH, 
            ["scripts/oura.py", "brief", date]
        )
        
        if not oura_data:
            return None
            
        # Extract key metrics
        sleep_data = oura_data.get("sleep", {})
        readiness_data = oura_data.get("readiness", {})
        
        return {
            "date": date,
            "sleep": {
                "score": sleep_data.get("score"),
                "total_sleep_hours": sleep_data.get("contributors", {}).get("total_sleep", 0) / 100.0 * 10,  # Rough conversion
                "efficiency": sleep_data.get("contributors", {}).get("efficiency"),
                "deep_sleep": sleep_data.get("contributors", {}).get("deep_sleep"),
                "rem_sleep": sleep_data.get("contributors", {}).get("rem_sleep"),
                "restfulness": sleep_data.get("contributors", {}).get("restfulness")
            },
            "readiness": {
                "score": readiness_data.get("score"),
                "hrv_balance": readiness_data.get("contributors", {}).get("hrv_balance"),
                "resting_heart_rate": readiness_data.get("contributors", {}).get("resting_heart_rate"),
                "sleep_balance": readiness_data.get("contributors", {}).get("sleep_balance"),
                "recovery_index": readiness_data.get("contributors", {}).get("recovery_index"),
                "temperature_deviation": readiness_data.get("temperature_deviation", 0)
            },
            "source": "oura",
            "collected_at": datetime.now().isoformat()
        }
    
    def collect_strava_data(self, limit: int = 10) -> List[Dict]:
        """Collect recent Strava runs."""
        strava_data = self._run_skill_command(
            STRAVA_SKILL_PATH,
            ["scripts/strava.py", "runs", str(limit)]
        )
        
        if not strava_data:
            return []
        
        runs = []
        for run in strava_data:
            # Extract relevant metrics
            pace_str = run.get("_pace_mi", "0:00/mi")
            try:
                # Convert pace string "8:42/mi" to decimal minutes
                pace_parts = pace_str.split("/")[0].split(":")
                pace_minutes = float(pace_parts[0]) + float(pace_parts[1]) / 60.0
            except:
                pace_minutes = 0.0
            
            runs.append({
                "date": run.get("_date"),
                "distance_miles": run.get("_distance_mi"),
                "duration_seconds": run.get("moving_time"),
                "pace_min_per_mile": pace_minutes,
                "average_hr": run.get("average_heartrate"),
                "max_hr": run.get("max_heartrate"),
                "elevation_gain": run.get("total_elevation_gain"),
                "suffer_score": run.get("suffer_score"),
                "strava_id": run.get("id"),
                "source": "strava",
                "collected_at": datetime.now().isoformat()
            })
        
        return runs
    
    def collect_daily_data(self, date: str = None) -> Dict:
        """Collect all data for a specific day."""
        if not date:
            date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        daily_data = {
            "date": date,
            "oura": None,
            "strava_runs": [],
            "collected_at": datetime.now().isoformat()
        }
        
        # Collect Oura data
        oura_data = self.collect_oura_data(date)
        if oura_data:
            daily_data["oura"] = oura_data
        
        # Collect Strava runs for this date
        recent_runs = self.collect_strava_data()
        daily_runs = [run for run in recent_runs if run.get("date") == date]
        daily_data["strava_runs"] = daily_runs
        
        return daily_data
    
    def store_daily_data(self, data: Dict):
        """Store daily data in historical collection."""
        date = data.get("date")
        if date:
            self.historical_data[date] = data
            self._save_historical_data()
            print(f"Stored data for {date}")
    
    def get_data_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get historical data for date range."""
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        data = []
        current_date = start
        while current_date <= end:
            date_str = current_date.strftime("%Y-%m-%d")
            if date_str in self.historical_data:
                data.append(self.historical_data[date_str])
            current_date += timedelta(days=1)
        
        return data
    
    def update_recent_data(self, days_back: int = 7):
        """Update data for recent days."""
        print(f"Updating health data for last {days_back} days...")
        
        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i+1)).strftime("%Y-%m-%d")
            daily_data = self.collect_daily_data(date)
            self.store_daily_data(daily_data)
        
        print("Data update complete")

if __name__ == "__main__":
    # Test the data collector
    collector = HealthDataCollector()
    
    print("Testing Oura data collection...")
    oura_test = collector.collect_oura_data()
    if oura_test:
        print(f"Oura data: Sleep {oura_test['sleep']['score']}, Readiness {oura_test['readiness']['score']}")
    
    print("Testing Strava data collection...")
    strava_test = collector.collect_strava_data(3)
    print(f"Found {len(strava_test)} recent runs")
    
    print("Testing daily data collection...")
    daily_test = collector.collect_daily_data()
    print(f"Daily data collected for {daily_test['date']}")
    
    print("Updating recent data...")
    collector.update_recent_data(3)
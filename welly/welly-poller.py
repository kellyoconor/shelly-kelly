#!/usr/bin/env python3
"""
Welly Poller - Continuous Oura/Strava Data Monitoring

Continuously polls Oura and Strava APIs for new data, integrating with existing
data ingestion pipeline while adding always-on capabilities.

Uses existing Oura/Strava skills and respects API rate limits.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import existing Welly ingest system
from welly_ingest import WellyIngest

class WellyPoller:
    """Continuous data polling that enhances existing Welly data ingestion"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        
        # Use existing Welly ingest system
        self.ingest = WellyIngest(workspace)
        
        # Polling configuration respecting API limits
        self.config = {
            "oura_poll_interval_hours": 4,  # Oura updates sleep data once daily
            "strava_poll_interval_hours": 2,  # Strava activities can come anytime
            "retry_interval_minutes": 30,  # Retry failed polls
            "max_retries": 3,
            "api_timeout_seconds": 30
        }
        
        self.state_file = self.workspace / "memory" / "welly_poller_state.json"
        
        # Skills paths
        self.oura_skill = self.workspace / "skills" / "oura" / "scripts" / "oura.py"
        self.strava_skill = self.workspace / "skills" / "strava" / "scripts" / "strava.py"
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def _load_polling_state(self) -> Dict:
        """Load persistent polling state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading polling state: {e}")
                
        return {
            "last_oura_poll": None,
            "last_strava_poll": None,
            "last_oura_data_hash": None,
            "last_strava_data_hash": None,
            "oura_poll_count": 0,
            "strava_poll_count": 0,
            "oura_consecutive_failures": 0,
            "strava_consecutive_failures": 0,
            "polling_since": datetime.now().isoformat()
        }
    
    def _save_polling_state(self, state: Dict):
        """Save persistent polling state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving polling state: {e}")
    
    async def _run_skill_command(self, skill_path: str, command: str, *args) -> Dict:
        """Run a skill command and return structured result"""
        try:
            cmd = ["python3", str(skill_path), command] + list(args)
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.workspace
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config["api_timeout_seconds"]
            )
            
            if process.returncode == 0:
                try:
                    return json.loads(stdout.decode())
                except json.JSONDecodeError:
                    return {"success": True, "raw_output": stdout.decode()}
            else:
                return {"error": f"Command failed: {stderr.decode()}"}
                
        except asyncio.TimeoutError:
            return {"error": "API request timed out"}
        except Exception as e:
            return {"error": f"Command execution failed: {str(e)}"}
    
    def _hash_data(self, data: Dict) -> str:
        """Create hash of data for change detection"""
        import hashlib
        
        # Convert to stable string representation
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    async def _poll_oura_data(self, state: Dict) -> Dict:
        """Poll Oura for new sleep/readiness data"""
        poll_result = {
            "success": False,
            "new_data": False,
            "data_types": [],
            "error": None
        }
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            
            # Get sleep data (usually available in morning)
            sleep_data = await self._run_skill_command(self.oura_skill, "sleep", yesterday)
            
            # Get readiness data
            readiness_data = await self._run_skill_command(self.oura_skill, "readiness", yesterday)
            
            # Get activity data
            activity_data = await self._run_skill_command(self.oura_skill, "activity", today)
            
            if (not sleep_data.get("error") or 
                not readiness_data.get("error") or 
                not activity_data.get("error")):
                
                poll_result["success"] = True
                
                # Check for new sleep data
                if not sleep_data.get("error") and sleep_data.get("data"):
                    sleep_hash = self._hash_data(sleep_data)
                    if sleep_hash != state.get("last_oura_sleep_hash"):
                        poll_result["new_data"] = True
                        poll_result["data_types"].append("sleep")
                        state["last_oura_sleep_hash"] = sleep_hash
                        
                        # Ingest through existing system
                        await self._ingest_oura_sleep(sleep_data, yesterday)
                
                # Check for new readiness data
                if not readiness_data.get("error") and readiness_data.get("data"):
                    readiness_hash = self._hash_data(readiness_data)
                    if readiness_hash != state.get("last_oura_readiness_hash"):
                        poll_result["new_data"] = True
                        poll_result["data_types"].append("readiness")
                        state["last_oura_readiness_hash"] = readiness_hash
                        
                        # Ingest through existing system
                        await self._ingest_oura_readiness(readiness_data, yesterday)
                
                # Check for new activity data
                if not activity_data.get("error") and activity_data.get("data"):
                    activity_hash = self._hash_data(activity_data)
                    if activity_hash != state.get("last_oura_activity_hash"):
                        poll_result["new_data"] = True
                        poll_result["data_types"].append("activity")
                        state["last_oura_activity_hash"] = activity_hash
                        
                        # Ingest through existing system  
                        await self._ingest_oura_activity(activity_data, today)
                
                state["oura_consecutive_failures"] = 0
                
            else:
                poll_result["error"] = "All Oura API calls failed"
                state["oura_consecutive_failures"] = state.get("oura_consecutive_failures", 0) + 1
            
        except Exception as e:
            poll_result["error"] = str(e)
            state["oura_consecutive_failures"] = state.get("oura_consecutive_failures", 0) + 1
            self.logger.error(f"Oura polling error: {e}")
        
        state["last_oura_poll"] = datetime.now().isoformat()
        state["oura_poll_count"] = state.get("oura_poll_count", 0) + 1
        
        return poll_result
    
    async def _ingest_oura_sleep(self, sleep_data: Dict, date_str: str):
        """Ingest Oura sleep data through existing system"""
        try:
            # Use existing ingest method but with fresh data
            result = self.ingest.ingest_oura_data(date_str)
            if not result.get("error"):
                self.logger.info(f"Ingested Oura sleep data for {date_str}")
        except Exception as e:
            self.logger.error(f"Error ingesting Oura sleep data: {e}")
    
    async def _ingest_oura_readiness(self, readiness_data: Dict, date_str: str):
        """Ingest Oura readiness data through existing system"""
        try:
            # The existing ingest_oura_data method handles readiness too
            result = self.ingest.ingest_oura_data(date_str)  
            if not result.get("error"):
                self.logger.info(f"Ingested Oura readiness data for {date_str}")
        except Exception as e:
            self.logger.error(f"Error ingesting Oura readiness data: {e}")
    
    async def _ingest_oura_activity(self, activity_data: Dict, date_str: str):
        """Ingest Oura activity data through existing system"""
        try:
            # The existing ingest_oura_data method handles activity too
            result = self.ingest.ingest_oura_data(date_str)
            if not result.get("error"):
                self.logger.info(f"Ingested Oura activity data for {date_str}")
        except Exception as e:
            self.logger.error(f"Error ingesting Oura activity data: {e}")
    
    async def _poll_strava_data(self, state: Dict) -> Dict:
        """Poll Strava for new activities"""
        poll_result = {
            "success": False,
            "new_data": False,
            "activities_found": 0,
            "error": None
        }
        
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get recent activities (last 7 days to catch any we missed)
            activities_data = await self._run_skill_command(self.strava_skill, "recent", "7")
            
            if not activities_data.get("error") and activities_data.get("data"):
                poll_result["success"] = True
                
                activities_hash = self._hash_data(activities_data)
                if activities_hash != state.get("last_strava_hash"):
                    poll_result["new_data"] = True
                    poll_result["activities_found"] = len(activities_data.get("data", []))
                    state["last_strava_hash"] = activities_hash
                    
                    # Ingest through existing system
                    await self._ingest_strava_activities(activities_data, today)
                
                state["strava_consecutive_failures"] = 0
                
            else:
                poll_result["error"] = activities_data.get("error", "No Strava data returned")
                state["strava_consecutive_failures"] = state.get("strava_consecutive_failures", 0) + 1
            
        except Exception as e:
            poll_result["error"] = str(e) 
            state["strava_consecutive_failures"] = state.get("strava_consecutive_failures", 0) + 1
            self.logger.error(f"Strava polling error: {e}")
        
        state["last_strava_poll"] = datetime.now().isoformat()
        state["strava_poll_count"] = state.get("strava_poll_count", 0) + 1
        
        return poll_result
    
    async def _ingest_strava_activities(self, activities_data: Dict, date_str: str):
        """Ingest Strava activities through existing system"""
        try:
            # Use existing ingest method
            result = self.ingest.ingest_strava_data(date_str)
            if not result.get("error"):
                self.logger.info(f"Ingested Strava activities for {date_str}")
        except Exception as e:
            self.logger.error(f"Error ingesting Strava activities: {e}")
    
    def _should_poll_oura(self, state: Dict) -> bool:
        """Check if it's time to poll Oura"""
        if not state.get("last_oura_poll"):
            return True
        
        last_poll = datetime.fromisoformat(state["last_oura_poll"])
        interval = timedelta(hours=self.config["oura_poll_interval_hours"])
        
        # If consecutive failures, use retry interval
        if state.get("oura_consecutive_failures", 0) > 0:
            interval = timedelta(minutes=self.config["retry_interval_minutes"])
        
        return datetime.now() - last_poll >= interval
    
    def _should_poll_strava(self, state: Dict) -> bool:
        """Check if it's time to poll Strava"""
        if not state.get("last_strava_poll"):
            return True
        
        last_poll = datetime.fromisoformat(state["last_strava_poll"])
        interval = timedelta(hours=self.config["strava_poll_interval_hours"])
        
        # If consecutive failures, use retry interval
        if state.get("strava_consecutive_failures", 0) > 0:
            interval = timedelta(minutes=self.config["retry_interval_minutes"])
        
        return datetime.now() - last_poll >= interval
    
    async def poll_all_sources(self) -> Dict:
        """Poll all data sources for updates"""
        state = self._load_polling_state()
        
        poll_result = {
            "oura_updated": False,
            "strava_updated": False,
            "oura_result": None,
            "strava_result": None,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Poll Oura if it's time
            if self._should_poll_oura(state):
                self.logger.info("Polling Oura for new data...")
                oura_result = await self._poll_oura_data(state)
                poll_result["oura_result"] = oura_result
                poll_result["oura_updated"] = oura_result.get("new_data", False)
            
            # Poll Strava if it's time
            if self._should_poll_strava(state):
                self.logger.info("Polling Strava for new activities...")
                strava_result = await self._poll_strava_data(state)
                poll_result["strava_result"] = strava_result
                poll_result["strava_updated"] = strava_result.get("new_data", False)
            
            self._save_polling_state(state)
            
        except Exception as e:
            self.logger.error(f"Error in poll_all_sources: {e}")
            poll_result["error"] = str(e)
        
        return poll_result
    
    def get_polling_status(self) -> Dict:
        """Get current polling status"""
        state = self._load_polling_state()
        
        return {
            "polling_since": state.get("polling_since"),
            "last_oura_poll": state.get("last_oura_poll"),
            "last_strava_poll": state.get("last_strava_poll"),
            "oura_poll_count": state.get("oura_poll_count", 0),
            "strava_poll_count": state.get("strava_poll_count", 0),
            "oura_consecutive_failures": state.get("oura_consecutive_failures", 0),
            "strava_consecutive_failures": state.get("strava_consecutive_failures", 0),
            "should_poll_oura": self._should_poll_oura(state),
            "should_poll_strava": self._should_poll_strava(state),
            "config": self.config
        }


def main():
    """CLI for testing poller functionality"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # Test polling functionality
            async def test_polling():
                poller = WellyPoller()
                print("🔄 Testing Welly Poller...")
                
                result = await poller.poll_all_sources()
                
                print(f"Oura updated: {result['oura_updated']}")
                print(f"Strava updated: {result['strava_updated']}")
                
                if result.get("oura_result"):
                    print(f"Oura result: {result['oura_result']}")
                if result.get("strava_result"):
                    print(f"Strava result: {result['strava_result']}")
            
            asyncio.run(test_polling())
            
        elif command == "status":
            poller = WellyPoller()
            status = poller.get_polling_status()
            
            print("🔄 Welly Poller Status")
            print(f"   Polling since: {status.get('polling_since', 'Never')}")
            print(f"   Last Oura poll: {status.get('last_oura_poll', 'Never')}")
            print(f"   Last Strava poll: {status.get('last_strava_poll', 'Never')}")
            print(f"   Oura polls: {status.get('oura_poll_count', 0)}")
            print(f"   Strava polls: {status.get('strava_poll_count', 0)}")
            print(f"   Oura failures: {status.get('oura_consecutive_failures', 0)}")
            print(f"   Strava failures: {status.get('strava_consecutive_failures', 0)}")
            print(f"   Should poll Oura: {status.get('should_poll_oura', False)}")
            print(f"   Should poll Strava: {status.get('should_poll_strava', False)}")
            
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-poller.py [test|status]")
    else:
        print("Welly Poller - Continuous Data Monitoring")
        print("Usage: python3 welly-poller.py [test|status]")


if __name__ == "__main__":
    main()
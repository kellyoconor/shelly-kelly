#!/usr/bin/env python3
"""
Welly Health Monitor - Watchdog for Always-On Components

Monitors the main Welly monitor and auto-restarts when it gets stuck.
Implements the three fixes Kelly requested:
1. Proper error recovery in polling loops
2. Health checks that detect when components stop working
3. Auto-restart of stuck polling
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

class WellyHealthMonitor:
    """Watches over Welly components and auto-restarts when stuck"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.config = {
            "health_check_interval_minutes": 5,  # Check every 5 minutes
            "max_data_poll_age_minutes": 60,     # Alert if no data poll in 1 hour
            "max_restart_attempts": 3,           # Max restarts per hour
            "restart_cooldown_minutes": 15       # Wait between restart attempts
        }
        
        self.state_file = self.workspace / "memory" / "welly_health_monitor.json"
        self.monitor_state_file = self.workspace / "memory" / "welly_monitor_state.json"
        self.poller_state_file = self.workspace / "memory" / "welly_poller_state.json"
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_health_state(self) -> Dict:
        """Load health monitor state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading health state: {e}")
        
        return {
            "started_at": datetime.now().isoformat(),
            "last_health_check": None,
            "restart_attempts_today": 0,
            "last_restart_attempt": None,
            "consecutive_failures": 0,
            "health_checks_completed": 0
        }
    
    def _save_health_state(self, state: Dict):
        """Save health monitor state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving health state: {e}")
    
    def _is_monitor_process_running(self) -> bool:
        """Check if monitor process is actually running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'welly-monitor.py'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _is_data_polling_stuck(self) -> Dict:
        """Check if data polling is stuck"""
        check_result = {
            "stuck": False,
            "reason": None,
            "last_poll_age_minutes": None,
            "monitor_running": False
        }
        
        # Check if monitor process is running
        check_result["monitor_running"] = self._is_monitor_process_running()
        
        if not check_result["monitor_running"]:
            check_result["stuck"] = True
            check_result["reason"] = "Monitor process not running"
            return check_result
        
        # Check monitor state for stuck data polling
        if self.monitor_state_file.exists():
            try:
                with open(self.monitor_state_file) as f:
                    monitor_state = json.load(f)
            except Exception as e:
                check_result["stuck"] = True
                check_result["reason"] = f"Error reading monitor state: {e}"
                return check_result
        else:
            check_result["stuck"] = True
            check_result["reason"] = "No monitor state file found"
            return check_result
        
        last_poll_str = monitor_state.get("last_data_poll")
        if not last_poll_str:
            check_result["stuck"] = True
            check_result["reason"] = "No data poll recorded"
            return check_result
        
        try:
            last_poll = datetime.fromisoformat(last_poll_str)
            age_minutes = (datetime.now() - last_poll).total_seconds() / 60
            check_result["last_poll_age_minutes"] = age_minutes
            
            if age_minutes > self.config["max_data_poll_age_minutes"]:
                check_result["stuck"] = True
                check_result["reason"] = f"Data poll too old: {age_minutes:.1f} minutes"
                
        except Exception as e:
            check_result["stuck"] = True
            check_result["reason"] = f"Error parsing poll time: {e}"
        
        return check_result
    
    def _can_attempt_restart(self, health_state: Dict) -> bool:
        """Check if we can attempt restart (not too many recent attempts)"""
        # Reset daily counter
        now = datetime.now()
        last_restart = health_state.get("last_restart_attempt")
        
        if last_restart:
            try:
                last_restart_dt = datetime.fromisoformat(last_restart)
                # Reset counter if it's a new day
                if last_restart_dt.date() != now.date():
                    health_state["restart_attempts_today"] = 0
                
                # Check cooldown period
                minutes_since_restart = (now - last_restart_dt).total_seconds() / 60
                if minutes_since_restart < self.config["restart_cooldown_minutes"]:
                    return False
                    
            except Exception:
                pass
        
        return health_state.get("restart_attempts_today", 0) < self.config["max_restart_attempts"]
    
    def _restart_welly_monitor(self, health_state: Dict) -> bool:
        """Restart the stuck Welly monitor"""
        try:
            self.logger.info("🔄 Attempting to restart stuck Welly monitor...")
            
            # Stop existing monitor
            subprocess.run(['pkill', '-f', 'welly-monitor.py'], 
                         capture_output=True)
            
            # Wait a moment
            time.sleep(3)
            
            # Start new monitor in background
            result = subprocess.Popen(
                ['python3', str(self.workspace / 'welly' / 'welly-monitor.py'), 'start'],
                cwd=self.workspace,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Update restart tracking
            health_state["last_restart_attempt"] = datetime.now().isoformat()
            health_state["restart_attempts_today"] = health_state.get("restart_attempts_today", 0) + 1
            
            self.logger.info(f"✅ Welly monitor restart initiated (attempt {health_state['restart_attempts_today']})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restart Welly monitor: {e}")
            return False
    
    async def _health_check_cycle(self):
        """Single health check cycle"""
        health_state = self._load_health_state()
        
        try:
            # Check if data polling is stuck
            stuck_check = self._is_data_polling_stuck()
            
            if stuck_check["stuck"]:
                self.logger.warning(f"🚨 Welly monitor stuck: {stuck_check['reason']}")
                health_state["consecutive_failures"] = health_state.get("consecutive_failures", 0) + 1
                
                # Attempt restart if allowed
                if self._can_attempt_restart(health_state):
                    restart_success = self._restart_welly_monitor(health_state)
                    if restart_success:
                        health_state["consecutive_failures"] = 0
                else:
                    self.logger.error("❌ Cannot restart: too many recent attempts or in cooldown")
            else:
                # System is healthy
                health_state["consecutive_failures"] = 0
                if stuck_check["last_poll_age_minutes"] is not None:
                    self.logger.info(f"✅ Welly monitor healthy (last poll {stuck_check['last_poll_age_minutes']:.1f}m ago)")
            
            health_state["last_health_check"] = datetime.now().isoformat()
            health_state["health_checks_completed"] = health_state.get("health_checks_completed", 0) + 1
            
        except Exception as e:
            self.logger.error(f"Health check cycle error: {e}")
            health_state["consecutive_failures"] = health_state.get("consecutive_failures", 0) + 1
        
        finally:
            self._save_health_state(health_state)
    
    async def run(self):
        """Main health monitoring loop"""
        self.logger.info("🩺 Welly Health Monitor starting...")
        print("🩺 Welly Health Monitor - Keeping Always-On systems healthy")
        print(f"   Checking every {self.config['health_check_interval_minutes']} minutes")
        print(f"   Auto-restart if no data poll in {self.config['max_data_poll_age_minutes']} minutes")
        print("   Press Ctrl+C to stop")
        
        while True:
            try:
                await self._health_check_cycle()
                
                # Sleep until next check
                sleep_seconds = self.config["health_check_interval_minutes"] * 60
                await asyncio.sleep(sleep_seconds)
                
            except KeyboardInterrupt:
                self.logger.info("Health monitor stopping...")
                break
            except Exception as e:
                self.logger.error(f"Health monitor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
        
        print("🩺 Welly Health Monitor stopped")
    
    def status(self) -> Dict:
        """Get health monitor status"""
        health_state = self._load_health_state()
        stuck_check = self._is_data_polling_stuck()
        
        return {
            "health_monitor": {
                "started_at": health_state.get("started_at"),
                "health_checks_completed": health_state.get("health_checks_completed", 0),
                "last_health_check": health_state.get("last_health_check"),
                "consecutive_failures": health_state.get("consecutive_failures", 0),
                "restart_attempts_today": health_state.get("restart_attempts_today", 0),
                "last_restart_attempt": health_state.get("last_restart_attempt")
            },
            "welly_monitor": {
                "process_running": stuck_check["monitor_running"],
                "stuck": stuck_check["stuck"],
                "stuck_reason": stuck_check["reason"],
                "last_poll_age_minutes": stuck_check["last_poll_age_minutes"]
            }
        }


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            monitor = WellyHealthMonitor()
            status = monitor.status()
            
            print("🩺 Welly Health Monitor Status")
            print(f"   Health checks: {status['health_monitor']['health_checks_completed']}")
            print(f"   Last check: {status['health_monitor']['last_health_check']}")
            print(f"   Consecutive failures: {status['health_monitor']['consecutive_failures']}")
            print(f"   Restart attempts today: {status['health_monitor']['restart_attempts_today']}")
            print("")
            print("💙 Welly Monitor Status")
            print(f"   Process running: {status['welly_monitor']['process_running']}")
            print(f"   Stuck: {status['welly_monitor']['stuck']}")
            if status['welly_monitor']['stuck_reason']:
                print(f"   Reason: {status['welly_monitor']['stuck_reason']}")
            if status['welly_monitor']['last_poll_age_minutes']:
                print(f"   Last poll: {status['welly_monitor']['last_poll_age_minutes']:.1f} minutes ago")
        
        elif command == "start":
            monitor = WellyHealthMonitor()
            asyncio.run(monitor.run())
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-health-monitor.py [start|status]")
    else:
        monitor = WellyHealthMonitor()
        asyncio.run(monitor.run())


if __name__ == "__main__":
    main()
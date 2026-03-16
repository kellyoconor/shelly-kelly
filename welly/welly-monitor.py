#!/usr/bin/env python3
"""
Welly Monitor - Always-On Pattern Detection Service

Persistent background service that continuously monitors Kelly's body-mind patterns,
learns from data in real-time, and surfaces gentle insights when meaningful patterns emerge.

This enhances the existing Welly system by making it always-on while preserving:
✅ Kelly's exact voice ("Your body's been whispering" style)
✅ Same data model and interpretation logic
✅ Same output format (What I'm noticing / What I'm wondering / Gentle nudge)
✅ All existing components (ingest, interpreter, memory, voice)
"""

import asyncio
import json
import logging
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Import existing Welly components
from welly_ingest import WellyIngest
from welly_interpreter import WellyInterpreter
from welly_memory import WellyMemory
from welly_voice import WellyVoice

# Import new always-on components  
# Use exec to handle file naming with dashes
import importlib.util

# Load welly-poller
spec = importlib.util.spec_from_file_location("welly_poller", "/data/workspace/welly/welly-poller.py")
welly_poller_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_poller_module)
WellyPoller = welly_poller_module.WellyPoller

# Load welly-patterns
spec = importlib.util.spec_from_file_location("welly_patterns", "/data/workspace/welly/welly-patterns.py")
welly_patterns_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_patterns_module)
WellyPatterns = welly_patterns_module.WellyPatterns

# Load welly-alerts
spec = importlib.util.spec_from_file_location("welly_alerts", "/data/workspace/welly/welly-alerts.py")
welly_alerts_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_alerts_module)
WellyAlerts = welly_alerts_module.WellyAlerts

class WellyMonitor:
    """Always-on Welly service that enhances existing manual check-in system"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.running = False
        
        # Initialize existing Welly components (no changes)
        self.ingest = WellyIngest(workspace)
        self.interpreter = WellyInterpreter(workspace)
        self.memory = WellyMemory(workspace)
        self.voice = WellyVoice()
        
        # Initialize new always-on components
        self.poller = WellyPoller(workspace)
        self.patterns = WellyPatterns(workspace)
        self.alerts = WellyAlerts(workspace)
        
        # Service configuration
        self.config = {
            "poll_interval_hours": 3,  # Check for new data every 3 hours
            "pattern_analysis_interval_hours": 6,  # Deep pattern analysis twice daily
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "08:00", 
            "weekend_mode": True,  # Gentler on weekends
            "max_alerts_per_day": 2,  # Don't overwhelm Kelly
            "alert_cooldown_hours": 8  # Space out alerts
        }
        
        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.state_file = self.workspace / "memory" / "welly_monitor_state.json"
        self.log_file = self.workspace / "memory" / "welly_monitor.log"
        
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def _load_state(self) -> Dict:
        """Load persistent monitor state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading state: {e}")
                
        return {
            "last_data_poll": None,
            "last_pattern_analysis": None,
            "last_alert_sent": None,
            "alerts_sent_today": 0,
            "current_day": None,
            "monitoring_since": datetime.now().isoformat()
        }
    
    def _save_state(self, state: Dict):
        """Save persistent monitor state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
    
    def _is_quiet_hours(self) -> bool:
        """Check if we're in Kelly's quiet hours"""
        now = datetime.now().time()
        quiet_start = datetime.strptime(self.config["quiet_hours_start"], "%H:%M").time()
        quiet_end = datetime.strptime(self.config["quiet_hours_end"], "%H:%M").time()
        
        if quiet_start < quiet_end:
            return quiet_start <= now <= quiet_end
        else:  # Overnight quiet period
            return now >= quiet_start or now <= quiet_end
    
    def _should_poll_data(self, state: Dict) -> bool:
        """Check if it's time to poll for new data"""
        if not state.get("last_data_poll"):
            return True
            
        last_poll = datetime.fromisoformat(state["last_data_poll"])
        poll_interval = timedelta(hours=self.config["poll_interval_hours"])
        
        return datetime.now() - last_poll >= poll_interval
    
    def _should_analyze_patterns(self, state: Dict) -> bool:
        """Check if it's time for deep pattern analysis"""
        if not state.get("last_pattern_analysis"):
            return True
            
        last_analysis = datetime.fromisoformat(state["last_pattern_analysis"])
        analysis_interval = timedelta(hours=self.config["pattern_analysis_interval_hours"])
        
        return datetime.now() - last_analysis >= analysis_interval
    
    def _can_send_alert(self, state: Dict) -> bool:
        """Check if we can send an alert (respects limits and cooldown)"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset daily counter if new day
        if state.get("current_day") != today:
            state["alerts_sent_today"] = 0
            state["current_day"] = today
        
        # Check daily limit
        if state["alerts_sent_today"] >= self.config["max_alerts_per_day"]:
            return False
        
        # Check cooldown period
        if state.get("last_alert_sent"):
            last_alert = datetime.fromisoformat(state["last_alert_sent"])
            cooldown = timedelta(hours=self.config["alert_cooldown_hours"])
            if datetime.now() - last_alert < cooldown:
                return False
        
        # No alerts during quiet hours
        if self._is_quiet_hours():
            return False
        
        return True
    
    async def _poll_and_process_data(self, state: Dict) -> Dict:
        """Poll for new data and process if found"""
        poll_result = {
            "new_data_found": False,
            "data_types": [],
            "interpretation_needed": False
        }
        
        try:
            # Use existing poller to check for new Oura/Strava data
            new_data = await self.poller.poll_all_sources()
            
            if new_data.get("oura_updated") or new_data.get("strava_updated"):
                poll_result["new_data_found"] = True
                
                if new_data.get("oura_updated"):
                    poll_result["data_types"].append("oura")
                if new_data.get("strava_updated"):
                    poll_result["data_types"].append("strava")
                
                # Process new data through existing Welly pipeline
                self.logger.info(f"New data found: {poll_result['data_types']}")
                
                # Use existing interpreter to analyze current state
                current_state = self.interpreter.interpret_daily_state()
                
                if current_state.get("confidence", 0) > 0.6:
                    poll_result["interpretation_needed"] = True
                    
                    # Learn patterns using existing memory system
                    self.memory.learn_from_daily_state(current_state)
                    
                    self.logger.info(f"State interpreted: {current_state.get('recovery_status')} / {current_state.get('mind_body_alignment')}")
            
            state["last_data_poll"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error polling data: {e}")
            poll_result["error"] = str(e)
        
        return poll_result
    
    async def _analyze_patterns(self, state: Dict) -> Dict:
        """Perform deep pattern analysis for alert-worthy insights"""
        analysis_result = {
            "patterns_detected": [],
            "alert_recommended": False,
            "alert_urgency": "normal"
        }
        
        try:
            # Use existing interpreter to get current state
            current_state = self.interpreter.interpret_daily_state()
            
            if current_state.get("confidence", 0) < 0.5:
                return analysis_result
            
            # Use new pattern engine to detect concerning trends
            pattern_insights = await self.patterns.analyze_concerning_patterns(current_state)
            
            if pattern_insights.get("concerning_patterns"):
                analysis_result["patterns_detected"] = pattern_insights["concerning_patterns"]
                analysis_result["alert_recommended"] = True
                analysis_result["alert_urgency"] = pattern_insights.get("urgency", "normal")
                
                self.logger.info(f"Concerning patterns detected: {len(pattern_insights['concerning_patterns'])}")
            
            state["last_pattern_analysis"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
            analysis_result["error"] = str(e)
        
        return analysis_result
    
    async def _generate_and_send_alert(self, patterns: Dict, state: Dict) -> bool:
        """Generate and send alert using Kelly's voice"""
        try:
            # Use existing interpreter and voice to generate Kelly-style message
            current_state = self.interpreter.interpret_daily_state()
            relevant_patterns = self.memory.get_relevant_patterns(current_state)
            
            # Use existing voice system to generate message in Kelly's style
            alert_message = self.voice.generate_daily_check_in(current_state, relevant_patterns)
            
            if alert_message:
                # Use new alert system to deliver message appropriately
                alert_sent = await self.alerts.send_gentle_alert(alert_message, patterns.get("urgency", "normal"))
                
                if alert_sent:
                    state["last_alert_sent"] = datetime.now().isoformat()
                    state["alerts_sent_today"] = state.get("alerts_sent_today", 0) + 1
                    
                    self.logger.info(f"Alert sent successfully: {alert_message[:50]}...")
                    return True
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
        
        return False
    
    async def _monitor_cycle(self):
        """Single monitoring cycle"""
        state = self._load_state()
        
        try:
            # 1. Check for new data and process
            if self._should_poll_data(state):
                poll_result = await self._poll_and_process_data(state)
                
                # 2. If new significant data, check for patterns
                if poll_result.get("interpretation_needed") or self._should_analyze_patterns(state):
                    pattern_result = await self._analyze_patterns(state)
                    
                    # 3. If concerning patterns found and alerts allowed, send gentle notification
                    if (pattern_result.get("alert_recommended") and 
                        self._can_send_alert(state)):
                        
                        await self._generate_and_send_alert(pattern_result, state)
            
            self._save_state(state)
            
        except Exception as e:
            self.logger.error(f"Monitor cycle error: {e}")
    
    async def run(self):
        """Main monitoring loop"""
        self.running = True
        self.logger.info("Welly Monitor starting - always-on pattern detection")
        
        print("💙 Welly Monitor starting...")
        print("   Monitoring Kelly's patterns in the background")
        print("   Preserving existing manual check-in system")
        print("   Press Ctrl+C to stop")
        
        while self.running:
            try:
                await self._monitor_cycle()
                
                # Sleep between cycles (30 minutes)
                for _ in range(30 * 60):  # 30 minutes in seconds
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                    
            except Exception as e:
                self.logger.error(f"Monitor loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
        
        self.logger.info("Welly Monitor stopped")
        print("💙 Welly Monitor stopped gracefully")
    
    def status(self) -> Dict:
        """Get current monitor status"""
        state = self._load_state()
        
        return {
            "running": self.running,
            "monitoring_since": state.get("monitoring_since"),
            "last_data_poll": state.get("last_data_poll"),
            "last_pattern_analysis": state.get("last_pattern_analysis"),
            "last_alert_sent": state.get("last_alert_sent"),
            "alerts_sent_today": state.get("alerts_sent_today", 0),
            "in_quiet_hours": self._is_quiet_hours(),
            "config": self.config
        }


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            monitor = WellyMonitor()
            status = monitor.status()
            
            print("💙 Welly Monitor Status")
            print(f"   Running: {status['running']}")
            print(f"   Monitoring since: {status.get('monitoring_since', 'Never')}")
            print(f"   Last data poll: {status.get('last_data_poll', 'Never')}")
            print(f"   Last pattern analysis: {status.get('last_pattern_analysis', 'Never')}")
            print(f"   Alerts sent today: {status.get('alerts_sent_today', 0)}")
            print(f"   In quiet hours: {status['in_quiet_hours']}")
            
        elif command == "start":
            # Run the monitor
            monitor = WellyMonitor()
            try:
                asyncio.run(monitor.run())
            except KeyboardInterrupt:
                print("\nShutting down...")
            
        elif command == "stop":
            # TODO: Implement proper process management
            print("To stop the monitor, use Ctrl+C or kill the process")
            
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-monitor.py [start|status|stop]")
    else:
        # Default to start if no command given
        monitor = WellyMonitor()
        try:
            asyncio.run(monitor.run())
        except KeyboardInterrupt:
            print("\nShutting down...")


if __name__ == "__main__":
    main()
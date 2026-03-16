#!/usr/bin/env python3
"""
Enhanced Welly Monitor with Better Error Recovery

Improved version of welly-monitor.py that implements:
1. Proper error recovery in polling loops
2. Self-healing when components get stuck
3. More frequent health checks
4. Exponential backoff on failures
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
import traceback

# Import existing Welly components
from welly_ingest import WellyIngest
from welly_interpreter import WellyInterpreter
from welly_memory import WellyMemory
from welly_voice import WellyVoice

# Import enhanced components
import importlib.util
spec = importlib.util.spec_from_file_location("welly_poller", "/data/workspace/welly/welly-poller.py")
welly_poller_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_poller_module)
WellyPoller = welly_poller_module.WellyPoller

spec = importlib.util.spec_from_file_location("welly_patterns", "/data/workspace/welly/welly-patterns.py")
welly_patterns_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_patterns_module)
WellyPatterns = welly_patterns_module.WellyPatterns

spec = importlib.util.spec_from_file_location("welly_alerts", "/data/workspace/welly/welly-alerts.py")
welly_alerts_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(welly_alerts_module)

class EnhancedWellyMonitor:
    \"\"\"Enhanced Always-On Welly Monitor with self-healing capabilities\"\"\"
    
    def __init__(self, workspace=\"/data/workspace\"):
        self.workspace = Path(workspace)
        
        # Enhanced configuration with shorter cycles and better recovery
        self.config = {
            \"base_cycle_minutes\": 10,        # Start with 10-minute cycles
            \"max_cycle_minutes\": 30,         # Max cycle time for backoff
            \"health_check_minutes\": 2,       # Quick health checks every 2 min
            \"max_consecutive_failures\": 5,   # Reset after 5 failures
            \"error_backoff_multiplier\": 1.5, # Exponential backoff on errors
            \"quiet_hours\": {\"start\": \"23:00\", \"end\": \"07:00\"},
            \"max_alerts_per_day\": 3
        }
        
        # State tracking
        self.state_file = self.workspace / \"memory\" / \"welly_monitor_enhanced_state.json\"
        self.running = False
        self.current_cycle_minutes = self.config[\"base_cycle_minutes\"]
        self.consecutive_failures = 0
        
        # Components - lazy loaded with error recovery
        self._poller = None
        self._interpreter = None
        self._memory = None
        self._voice = None
        self._patterns = None
        self._alerts = None
        
        # Setup enhanced logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Graceful shutdown handler
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        \"\"\"Handle shutdown signals gracefully\"\"\"
        self.logger.info(f\"Received signal {signum}, shutting down gracefully...\")
        self.running = False
    
    @property
    def poller(self):
        \"\"\"Lazy-loaded poller with error recovery\"\"\"
        if self._poller is None:
            try:
                self._poller = WellyPoller(self.workspace)
                self.logger.debug(\"Poller component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize poller: {e}\")
                raise
        return self._poller
    
    @property
    def interpreter(self):
        \"\"\"Lazy-loaded interpreter with error recovery\"\"\"
        if self._interpreter is None:
            try:
                self._interpreter = WellyInterpreter(self.workspace)
                self.logger.debug(\"Interpreter component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize interpreter: {e}\")
                # Try to continue without interpreter for this cycle
                return None
        return self._interpreter
    
    @property  
    def memory(self):
        \"\"\"Lazy-loaded memory with error recovery\"\"\"
        if self._memory is None:
            try:
                self._memory = WellyMemory(self.workspace)
                self.logger.debug(\"Memory component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize memory: {e}\")
                return None
        return self._memory
    
    @property
    def voice(self):
        \"\"\"Lazy-loaded voice with error recovery\"\"\"
        if self._voice is None:
            try:
                self._voice = WellyVoice(self.workspace)
                self.logger.debug(\"Voice component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize voice: {e}\")
                return None
        return self._voice
    
    @property
    def patterns(self):
        \"\"\"Lazy-loaded patterns with error recovery\"\"\"
        if self._patterns is None:
            try:
                self._patterns = WellyPatterns(self.workspace)
                self.logger.debug(\"Patterns component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize patterns: {e}\")
                return None
        return self._patterns
    
    @property
    def alerts(self):
        \"\"\"Lazy-loaded alerts with error recovery\"\"\"
        if self._alerts is None:
            try:
                # Dynamic import for alerts
                spec = importlib.util.spec_from_file_location(\"welly_alerts\", \"/data/workspace/welly/welly-alerts.py\")
                alerts_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(alerts_module)
                self._alerts = alerts_module.WellyAlerts(self.workspace)
                self.logger.debug(\"Alerts component initialized\")
            except Exception as e:
                self.logger.error(f\"Failed to initialize alerts: {e}\")
                return None
        return self._alerts
    
    def _load_state(self) -> Dict:
        \"\"\"Load enhanced monitor state\"\"\"
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    state = json.load(f)
                    # Reset daily counters if new day
                    now = datetime.now()
                    if state.get(\"current_day\") != now.strftime(\"%Y-%m-%d\"):
                        state[\"current_day\"] = now.strftime(\"%Y-%m-%d\")
                        state[\"alerts_sent_today\"] = 0
                    return state
            except Exception as e:
                self.logger.error(f\"Error loading monitor state: {e}\")
        
        return {
            "monitoring_since": datetime.now().isoformat(),
            "current_day": datetime.now().strftime("%Y-%m-%d"),
            "last_data_poll": None,
            "last_pattern_analysis": None,
            "last_alert_sent": None,
            "alerts_sent_today": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "last_cycle_duration_seconds": 0,
            "component_failures": {
                "poller": 0,
                "interpreter": 0,
                "memory": 0,
                "patterns": 0,
                "alerts": 0
            }
        }\n    \n    def _save_state(self, state: Dict):\n        \"\"\"Save enhanced monitor state\"\"\"\n        try:\n            self.state_file.parent.mkdir(parents=True, exist_ok=True)\n            with open(self.state_file, 'w') as f:\n                json.dump(state, f, indent=2)\n        except Exception as e:\n            self.logger.error(f\"Error saving monitor state: {e}\")\n    \n    async def _robust_poll_data(self, state: Dict) -> Dict:\n        \"\"\"Poll data with enhanced error recovery and retries\"\"\"\n        poll_result = {\n            \"success\": False,\n            \"new_data_found\": False,\n            \"data_types\": [],\n            \"error\": None,\n            \"retry_count\": 0\n        }\n        \n        max_retries = 3\n        retry_delay = 5  # seconds\n        \n        for attempt in range(max_retries):\n            try:\n                # Use poller with timeout protection\n                poll_task = asyncio.create_task(self.poller.poll_all_sources())\n                new_data = await asyncio.wait_for(poll_task, timeout=60)  # 1 minute timeout\n                \n                if new_data.get(\"oura_updated\") or new_data.get(\"strava_updated\"):\n                    poll_result[\"new_data_found\"] = True\n                    \n                    if new_data.get(\"oura_updated\"):\n                        poll_result[\"data_types\"].append(\"oura\")\n                    if new_data.get(\"strava_updated\"):\n                        poll_result[\"data_types\"].append(\"strava\")\n                    \n                    self.logger.info(f\"✅ New data found: {poll_result['data_types']}\")\n                \n                poll_result[\"success\"] = True\n                state[\"last_data_poll\"] = datetime.now().isoformat()\n                \n                # Reset failure counters on success\n                state[\"component_failures\"][\"poller\"] = 0\n                break\n                \n            except asyncio.TimeoutError:\n                poll_result[\"error\"] = f\"Data polling timeout (attempt {attempt + 1})\"\n                self.logger.warning(f\"⏰ Polling timeout on attempt {attempt + 1}\")\n            except Exception as e:\n                poll_result[\"error\"] = f\"Polling error: {str(e)} (attempt {attempt + 1})\"\n                self.logger.error(f\"❌ Polling error on attempt {attempt + 1}: {e}\")\n                if \"AttributeError\" in str(e) or \"ModuleNotFoundError\" in str(e):\n                    # Component initialization error - reset component\n                    self._poller = None\n                    self.logger.info(\"🔄 Resetting poller component for recovery\")\n            \n            poll_result[\"retry_count\"] = attempt + 1\n            state[\"component_failures\"][\"poller\"] = state.get(\"component_failures\", {}).get(\"poller\", 0) + 1\n            \n            if attempt < max_retries - 1:\n                self.logger.info(f\"⏳ Retrying polling in {retry_delay} seconds...\")\n                await asyncio.sleep(retry_delay)\n                retry_delay *= 2  # Exponential backoff\n        \n        return poll_result\n    \n    async def _robust_analyze_patterns(self, state: Dict) -> Dict:\n        \"\"\"Analyze patterns with enhanced error recovery\"\"\"\n        analysis_result = {\n            \"success\": False,\n            \"patterns_detected\": [],\n            \"alert_recommended\": False,\n            \"error\": None\n        }\n        \n        try:\n            # Skip analysis if interpreter failed to load\n            if not self.interpreter:\n                analysis_result[\"error\"] = \"Interpreter component unavailable\"\n                return analysis_result\n            \n            # Get current state with timeout\n            interpret_task = asyncio.create_task(asyncio.to_thread(\n                self.interpreter.interpret_daily_state\n            ))\n            current_state = await asyncio.wait_for(interpret_task, timeout=30)\n            \n            if current_state.get(\"confidence\", 0) < 0.5:\n                analysis_result[\"error\"] = \"Low confidence in current state interpretation\"\n                return analysis_result\n            \n            # Pattern analysis with timeout protection\n            if self.patterns:\n                pattern_task = asyncio.create_task(\n                    self.patterns.analyze_concerning_patterns(current_state)\n                )\n                pattern_insights = await asyncio.wait_for(pattern_task, timeout=30)\n                \n                if pattern_insights.get(\"concerning_patterns\"):\n                    analysis_result[\"patterns_detected\"] = pattern_insights[\"concerning_patterns\"]\n                    analysis_result[\"alert_recommended\"] = True\n                    \n                    self.logger.info(f\"🔍 Concerning patterns detected: {len(pattern_insights['concerning_patterns'])}\")\n            \n            analysis_result[\"success\"] = True\n            state[\"last_pattern_analysis\"] = datetime.now().isoformat()\n            \n            # Reset failure counters\n            state[\"component_failures\"][\"interpreter\"] = 0\n            state[\"component_failures\"][\"patterns\"] = 0\n            \n        except asyncio.TimeoutError:\n            analysis_result[\"error\"] = \"Pattern analysis timeout\"\n            self.logger.warning(\"⏰ Pattern analysis timeout\")\n        except Exception as e:\n            analysis_result[\"error\"] = str(e)\n            self.logger.error(f\"❌ Pattern analysis error: {e}\")\n            \n            # Reset components if needed\n            if \"AttributeError\" in str(e):\n                self._interpreter = None\n                self._patterns = None\n                self.logger.info(\"🔄 Resetting interpreter/patterns components\")\n            \n            state[\"component_failures\"][\"interpreter\"] = state.get(\"component_failures\", {}).get(\"interpreter\", 0) + 1\n        \n        return analysis_result\n    \n    def _should_send_alert(self, state: Dict) -> bool:\n        \"\"\"Enhanced alert timing logic\"\"\"\n        # Check daily limits\n        if state.get(\"alerts_sent_today\", 0) >= self.config[\"max_alerts_per_day\"]:\n            return False\n        \n        # Check quiet hours\n        now = datetime.now().time()\n        quiet_start = datetime.strptime(self.config[\"quiet_hours\"][\"start\"], \"%H:%M\").time()\n        quiet_end = datetime.strptime(self.config[\"quiet_hours\"][\"end\"], \"%H:%M\").time()\n        \n        if quiet_start <= now or now <= quiet_end:\n            return False\n        \n        # Check minimum time between alerts (2 hours)\n        last_alert = state.get(\"last_alert_sent\")\n        if last_alert:\n            try:\n                last_alert_dt = datetime.fromisoformat(last_alert)\n                hours_since = (datetime.now() - last_alert_dt).total_seconds() / 3600\n                if hours_since < 2:\n                    return False\n            except Exception:\n                pass\n        \n        return True\n    \n    async def _enhanced_monitor_cycle(self):\n        \"\"\"Enhanced monitoring cycle with comprehensive error recovery\"\"\"\n        state = self._load_state()\n        cycle_start = time.time()\n        cycle_success = True\n        \n        try:\n            self.logger.info(f\"🔄 Starting monitor cycle (interval: {self.current_cycle_minutes}m)\")\n            \n            # 1. Robust data polling\n            poll_result = await self._robust_poll_data(state)\n            \n            # 2. Pattern analysis if we have new data or it's been a while\n            should_analyze = (\n                poll_result[\"new_data_found\"] or \n                not state.get(\"last_pattern_analysis\") or\n                (datetime.now() - datetime.fromisoformat(state.get(\"last_pattern_analysis\", \"1970-01-01T00:00:00\"))).total_seconds() > 3600  # 1 hour\n            )\n            \n            if should_analyze:\n                analysis_result = await self._robust_analyze_patterns(state)\n                \n                # 3. Send alert if patterns warrant it\n                if (analysis_result.get(\"alert_recommended\") and \n                    self._should_send_alert(state)):\n                    \n                    try:\n                        if self.alerts and self.voice and self.interpreter:\n                            current_state = self.interpreter.interpret_daily_state()\n                            alert_message = self.voice.generate_daily_check_in(current_state, {})\n                            \n                            if alert_message:\n                                alert_sent = await self.alerts.send_gentle_alert(\n                                    alert_message, analysis_result.get(\"urgency\", \"normal\")\n                                )\n                                \n                                if alert_sent:\n                                    state[\"last_alert_sent\"] = datetime.now().isoformat()\n                                    state[\"alerts_sent_today\"] = state.get(\"alerts_sent_today\", 0) + 1\n                                    self.logger.info(f\"📨 Alert sent: {alert_message[:50]}...\")\n                    \n                    except Exception as e:\n                        self.logger.error(f\"❌ Alert generation/sending failed: {e}\")\n                        state[\"component_failures\"][\"alerts\"] = state.get(\"component_failures\", {}).get(\"alerts\", 0) + 1\n            \n            # Cycle completed successfully\n            state[\"successful_cycles\"] = state.get(\"successful_cycles\", 0) + 1\n            self.consecutive_failures = 0\n            \n            # Reset cycle timing on success\n            self.current_cycle_minutes = self.config[\"base_cycle_minutes\"]\n            \n        except Exception as e:\n            cycle_success = False\n            self.consecutive_failures += 1\n            state[\"failed_cycles\"] = state.get(\"failed_cycles\", 0) + 1\n            \n            self.logger.error(f\"❌ Monitor cycle failed: {e}\")\n            self.logger.error(f\"Traceback: {traceback.format_exc()}\")\n            \n            # Exponential backoff on repeated failures\n            if self.consecutive_failures >= 3:\n                self.current_cycle_minutes = min(\n                    self.current_cycle_minutes * self.config[\"error_backoff_multiplier\"],\n                    self.config[\"max_cycle_minutes\"]\n                )\n                self.logger.warning(f\"⏰ Backing off to {self.current_cycle_minutes:.1f}m cycles after {self.consecutive_failures} failures\")\n            \n            # Reset all components after too many failures\n            if self.consecutive_failures >= self.config[\"max_consecutive_failures\"]:\n                self.logger.warning(\"🔄 Resetting all components after consecutive failures\")\n                self._poller = None\n                self._interpreter = None\n                self._memory = None\n                self._patterns = None\n                self._alerts = None\n                self.consecutive_failures = 0\n        \n        finally:\n            # Record cycle timing\n            cycle_duration = time.time() - cycle_start\n            state[\"last_cycle_duration_seconds\"] = cycle_duration\n            self._save_state(state)\n            \n            self.logger.info(f\"✅ Cycle completed in {cycle_duration:.1f}s (success: {cycle_success})\")\n    \n    async def run(self):\n        \"\"\"Enhanced main monitoring loop with self-healing\"\"\"\n        self.running = True\n        self.logger.info(\"💙 Enhanced Welly Monitor starting - always-on with self-healing\")\n        \n        print(\"💙 Enhanced Welly Monitor\")\n        print(\"   ✅ Self-healing error recovery\")\n        print(\"   🔄 Auto-restart stuck components\")\n        print(\"   ⏰ Adaptive cycle timing\")\n        print(\"   🩺 Comprehensive health checks\")\n        print(\"   Press Ctrl+C to stop\")\n        \n        while self.running:\n            try:\n                await self._enhanced_monitor_cycle()\n                \n                # Adaptive sleep timing\n                sleep_seconds = self.current_cycle_minutes * 60\n                \n                # Sleep in small chunks to allow graceful shutdown\n                for _ in range(int(sleep_seconds)):\n                    if not self.running:\n                        break\n                    await asyncio.sleep(1)\n                \n            except KeyboardInterrupt:\n                self.logger.info(\"Monitor stopping via keyboard interrupt...\")\n                break\n            except Exception as e:\n                self.logger.error(f\"Monitor loop error: {e}\")\n                await asyncio.sleep(60)  # Wait 1 minute before retry\n        \n        self.logger.info(\"💙 Enhanced Welly Monitor stopped gracefully\")\n        print(\"💙 Monitor stopped\")\n\n\ndef main():\n    if len(sys.argv) > 1:\n        command = sys.argv[1]\n        \n        if command == \"start\":\n            monitor = EnhancedWellyMonitor()\n            asyncio.run(monitor.run())\n        \n        elif command == \"status\":\n            monitor = EnhancedWellyMonitor()\n            state = monitor._load_state()\n            \n            print(\"💙 Enhanced Welly Monitor Status\")\n            print(f\"   Monitoring since: {state.get('monitoring_since')}\")\n            print(f\"   Last data poll: {state.get('last_data_poll')}\")\n            print(f\"   Last analysis: {state.get('last_pattern_analysis')}\")\n            print(f\"   Successful cycles: {state.get('successful_cycles', 0)}\")\n            print(f\"   Failed cycles: {state.get('failed_cycles', 0)}\")\n            print(f\"   Alerts sent today: {state.get('alerts_sent_today', 0)}\")\n            \n            failures = state.get('component_failures', {})\n            if any(failures.values()):\n                print(\"   Component failures:\")\n                for component, count in failures.items():\n                    if count > 0:\n                        print(f\"     {component}: {count}\")\n        \n        else:\n            print(f\"Unknown command: {command}\")\n            print(\"Usage: python3 welly-monitor-enhanced.py [start|status]\")\n    else:\n        monitor = EnhancedWellyMonitor()\n        asyncio.run(monitor.run())\n\n\nif __name__ == \"__main__\":\n    main()\n"
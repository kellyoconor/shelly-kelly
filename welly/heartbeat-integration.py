#!/usr/bin/env python3
"""
Heartbeat Integration for Always-On Welly

Integrates the always-on Welly service with the existing heartbeat system.
This allows both systems to work together:
- Always-on service monitors patterns continuously
- Heartbeat system can trigger manual check-ins and status updates
- Both systems respect Kelly's preferences and don't duplicate alerts
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Import existing Welly components
from welly import Welly
from welly_heartbeat import WellyHeartbeat

class WellyHeartbeatIntegration:
    """Integration layer between heartbeat system and always-on service"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        
        # Initialize both systems
        self.welly = Welly(workspace)
        self.heartbeat = WellyHeartbeat(workspace)
        
        self.integration_state_file = self.workspace / "memory" / "welly_heartbeat_integration.json"
        
    def _load_integration_state(self) -> Dict:
        """Load heartbeat integration state"""
        if self.integration_state_file.exists():
            try:
                with open(self.integration_state_file) as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "last_heartbeat_check": None,
            "last_manual_checkin_prompt": None,
            "heartbeat_count": 0,
            "always_on_alerts_received": 0,
            "integration_mode": "collaborative"  # both systems work together
        }
    
    def _save_integration_state(self, state: Dict):
        """Save heartbeat integration state"""
        try:
            self.integration_state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.integration_state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving integration state: {e}")
    
    def _is_always_on_service_running(self) -> bool:
        """Check if the always-on service is running"""
        try:
            result = subprocess.run([
                "systemctl", "is-active", "welly-monitor"
            ], capture_output=True, text=True)
            
            return result.returncode == 0 and result.stdout.strip() == "active"
        except:
            return False
    
    def _get_always_on_status(self) -> Dict:
        """Get status from always-on components"""
        status = {
            "monitor_running": False,
            "last_alert": None,
            "alerts_sent_today": 0,
            "recent_patterns": [],
            "error": None
        }
        
        try:
            # Check monitor status
            monitor_result = subprocess.run([
                "python3", str(self.workspace / "welly" / "welly-monitor.py"), "status"
            ], capture_output=True, text=True, timeout=10)
            
            if monitor_result.returncode == 0:
                status["monitor_running"] = True
            
            # Check alert status  
            alert_result = subprocess.run([
                "python3", str(self.workspace / "welly" / "welly-alerts.py"), "status"
            ], capture_output=True, text=True, timeout=10)
            
            if alert_result.returncode == 0:
                # Parse alert status output
                for line in alert_result.stdout.split('\n'):
                    if "Alerts today:" in line:
                        try:
                            alerts_today = int(line.split('/')[-1])
                            status["alerts_sent_today"] = alerts_today
                        except:
                            pass
            
        except Exception as e:
            status["error"] = str(e)
        
        return status
    
    def should_run_manual_checkin(self) -> Dict:
        """Determine if heartbeat should prompt for manual check-in"""
        state = self._load_integration_state()
        always_on_status = self._get_always_on_status()
        
        result = {
            "should_prompt": False,
            "reason": None,
            "message": None,
            "urgency": "normal"
        }
        
        try:
            # If always-on service is running and recently sent alerts, be less pushy
            if (self._is_always_on_service_running() and 
                always_on_status["alerts_sent_today"] > 0):
                
                # Always-on service is handling things, be quieter
                result["reason"] = "always_on_active"
                return result
            
            # Check if it's been too long since manual check-in
            last_manual = state.get("last_manual_checkin_prompt")
            if last_manual:
                last_manual_dt = datetime.fromisoformat(last_manual)
                time_since_last = datetime.now() - last_manual_dt
                
                # If always-on is running, be less frequent (every 3 days vs daily)
                threshold_days = 3 if self._is_always_on_service_running() else 1
                
                if time_since_last >= timedelta(days=threshold_days):
                    result["should_prompt"] = True
                    result["reason"] = f"time_since_last_{threshold_days}d"
                    result["message"] = self.welly.voice.generate_manual_checkin_prompt()
            else:
                # No previous manual check-in
                result["should_prompt"] = True
                result["reason"] = "no_previous_checkin"
                result["message"] = self.welly.voice.generate_manual_checkin_prompt()
            
            # Update state if prompting
            if result["should_prompt"]:
                state["last_manual_checkin_prompt"] = datetime.now().isoformat()
                self._save_integration_state(state)
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def coordinate_with_always_on(self) -> Dict:
        """Coordinate heartbeat activities with always-on service"""
        state = self._load_integration_state()
        coordination_result = {
            "action_taken": None,
            "message": None,
            "always_on_status": None,
            "heartbeat_action": "continue"  # or "skip"
        }
        
        try:
            # Get always-on status
            always_on_status = self._get_always_on_status()
            coordination_result["always_on_status"] = always_on_status
            
            # If always-on service is handling alerts, heartbeat can be lighter
            if (always_on_status["monitor_running"] and 
                always_on_status["alerts_sent_today"] > 0):
                
                coordination_result["action_taken"] = "defer_to_always_on"
                coordination_result["heartbeat_action"] = "skip"
                coordination_result["message"] = "Always-on service is actively monitoring"
                
            # If always-on service isn't running, heartbeat should be more active
            elif not always_on_status["monitor_running"]:
                coordination_result["action_taken"] = "heartbeat_primary"
                coordination_result["message"] = "Heartbeat taking primary monitoring role"
            
            # Collaborative mode - both systems work together
            else:
                coordination_result["action_taken"] = "collaborative"
                coordination_result["message"] = "Both systems active and coordinated"
            
            state["heartbeat_count"] = state.get("heartbeat_count", 0) + 1
            state["last_heartbeat_check"] = datetime.now().isoformat()
            self._save_integration_state(state)
            
        except Exception as e:
            coordination_result["error"] = str(e)
        
        return coordination_result
    
    def run_integrated_heartbeat(self) -> Dict:
        """Run heartbeat cycle integrated with always-on service"""
        heartbeat_result = {
            "timestamp": datetime.now().isoformat(),
            "integration_active": True,
            "actions_taken": [],
            "messages_sent": [],
            "coordination_result": None
        }
        
        try:
            # Step 1: Coordinate with always-on service
            coordination = self.coordinate_with_always_on()
            heartbeat_result["coordination_result"] = coordination
            
            # Step 2: Decide on heartbeat actions based on coordination
            if coordination["heartbeat_action"] == "skip":
                heartbeat_result["actions_taken"].append("skipped_due_to_always_on")
                return heartbeat_result
            
            # Step 3: Check if manual check-in needed
            manual_checkin = self.should_run_manual_checkin()
            
            if manual_checkin["should_prompt"] and manual_checkin.get("message"):
                heartbeat_result["actions_taken"].append("manual_checkin_prompt")
                heartbeat_result["messages_sent"].append({
                    "type": "manual_checkin_prompt",
                    "message": manual_checkin["message"],
                    "urgency": manual_checkin.get("urgency", "normal")
                })
            
            # Step 4: Run light data check (don't duplicate always-on polling)
            if coordination["action_taken"] != "defer_to_always_on":
                # Only do light checks that complement always-on monitoring
                state_check = self.welly.get_current_state()
                
                if state_check.get("confidence", 0) > 0.7:
                    heartbeat_result["actions_taken"].append("state_check_completed")
                    
                    # Only generate message if always-on hasn't already alerted
                    always_on_status = coordination.get("always_on_status", {})
                    if always_on_status.get("alerts_sent_today", 0) == 0:
                        
                        # Use existing heartbeat logic but be gentler
                        patterns = self.welly.get_patterns()
                        if any(pattern.get("confidence", 0) > 0.8 for pattern_list in patterns.values() for pattern in pattern_list):
                            
                            # Generate gentle message using existing voice
                            gentle_message = self.welly.voice.generate_daily_check_in(
                                state_check, 
                                patterns
                            )
                            
                            if gentle_message:
                                heartbeat_result["actions_taken"].append("gentle_pattern_message")
                                heartbeat_result["messages_sent"].append({
                                    "type": "pattern_insight",
                                    "message": gentle_message,
                                    "urgency": "low"
                                })
            
        except Exception as e:
            heartbeat_result["error"] = str(e)
        
        return heartbeat_result
    
    def get_integration_status(self) -> Dict:
        """Get comprehensive integration status"""
        state = self._load_integration_state()
        
        return {
            "integration_active": True,
            "always_on_running": self._is_always_on_service_running(),
            "integration_mode": state.get("integration_mode", "collaborative"),
            "last_heartbeat": state.get("last_heartbeat_check"),
            "heartbeat_count": state.get("heartbeat_count", 0),
            "last_manual_prompt": state.get("last_manual_checkin_prompt"),
            "always_on_status": self._get_always_on_status()
        }


def generate_heartbeat_md_integration() -> str:
    """Generate HEARTBEAT.md integration code"""
    
    integration_code = '''
## Welly Integration (Always-On Compatible)

```python
import sys
sys.path.append('/data/workspace/welly')

try:
    from heartbeat_integration import WellyHeartbeatIntegration
    
    # Initialize integrated system
    welly_integration = WellyHeartbeatIntegration()
    
    # Run coordinated heartbeat (works with or without always-on service)
    heartbeat_result = welly_integration.run_integrated_heartbeat()
    
    # Send any messages generated
    for message_data in heartbeat_result.get("messages_sent", []):
        message_text = message_data["message"]
        message_type = message_data["type"]
        
        if message_type == "manual_checkin_prompt":
            print(f"💙 Welly Check-in: {message_text}")
        elif message_type == "pattern_insight":
            print(f"💙 Welly: {message_text}")
    
    # Log coordination info for debugging
    coordination = heartbeat_result.get("coordination_result", {})
    if coordination.get("message"):
        # Uncomment for debugging: print(f"Debug: {coordination['message']}")
        pass
        
except ImportError:
    # Fallback to original Welly if integration not available
    from welly import Welly
    
    welly = Welly()
    
    # Original heartbeat logic
    if welly.heartbeat.should_run_today():
        result = welly.daily_check_in()
        
        if result.get("should_check_in") and result.get("check_in_message"):
            print(f"💙 Welly: {result['check_in_message']}")
            
except Exception as e:
    # Silent fallback - don't break heartbeat system
    pass
```

**Integration Notes:**
- Works with or without always-on service
- Automatically coordinates to avoid duplicate alerts
- Falls back gracefully if always-on components unavailable  
- Preserves existing manual check-in system
- Respects Kelly's alert frequency preferences
'''
    
    return integration_code


def main():
    """CLI for testing integration"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        integration = WellyHeartbeatIntegration()
        
        if command == "test":
            # Test integrated heartbeat
            result = integration.run_integrated_heartbeat()
            
            print("🔄 Integrated Heartbeat Test Results:")
            print(f"   Integration active: {result['integration_active']}")
            print(f"   Actions taken: {result.get('actions_taken', [])}")
            
            if result.get("messages_sent"):
                print("   Messages:")
                for msg in result["messages_sent"]:
                    print(f"     {msg['type']}: {msg['message'][:100]}...")
            
            coordination = result.get("coordination_result", {})
            if coordination:
                print(f"   Coordination: {coordination.get('action_taken', 'unknown')}")
        
        elif command == "status":
            status = integration.get_integration_status()
            
            print("💙 Welly Integration Status")
            print(f"   Always-on running: {status['always_on_running']}")
            print(f"   Integration mode: {status['integration_mode']}")
            print(f"   Heartbeat count: {status['heartbeat_count']}")
            print(f"   Last heartbeat: {status.get('last_heartbeat', 'Never')}")
            print(f"   Last manual prompt: {status.get('last_manual_prompt', 'Never')}")
        
        elif command == "generate":
            # Generate HEARTBEAT.md integration code
            integration_code = generate_heartbeat_md_integration()
            
            print("Generated HEARTBEAT.md Integration Code:")
            print("="*50)
            print(integration_code)
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 heartbeat-integration.py [test|status|generate]")
    else:
        print("Welly Heartbeat Integration")
        print("Usage: python3 heartbeat-integration.py [test|status|generate]")


if __name__ == "__main__":
    main()
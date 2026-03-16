#!/usr/bin/env python3
"""
Welly Alerts - Smart Alerting System

Delivers gentle, Kelly-style alerts only when patterns warrant attention.
Uses existing voice system to maintain Kelly's communication style and preferences.

Respects quiet hours, alert frequency limits, and Kelly's preference for non-overwhelming notifications.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import existing Welly voice system
from welly_voice import WellyVoice

class WellyAlerts:
    """Smart alerting that uses Kelly's voice and respects her preferences"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        
        # Use existing voice system for Kelly's style
        self.voice = WellyVoice()
        
        # Kelly's alert preferences
        self.alert_config = {
            "preferred_channel": "whatsapp",  # Kelly's main channel
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "08:00",
            "max_alerts_per_day": 2,  # Don't overwhelm
            "cooldown_hours": 8,  # Space out alerts
            "weekend_gentler": True,  # Lighter touch on weekends
            "urgent_override": False,  # Even urgent alerts respect quiet/limits
            "escalation_enabled": False  # Kelly doesn't want escalation
        }
        
        self.state_file = self.workspace / "memory" / "welly_alerts_state.json"
        
        # Alert delivery methods
        self.delivery_methods = {
            "whatsapp": self._send_whatsapp_message,
            "file": self._write_to_file,
            "log": self._log_alert
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _load_alert_state(self) -> Dict:
        """Load persistent alert state"""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading alert state: {e}")
        
        return {
            "alerts_sent_today": 0,
            "current_date": None,
            "last_alert_time": None,
            "total_alerts_sent": 0,
            "alert_history": [],
            "cooldown_until": None
        }
    
    def _save_alert_state(self, state: Dict):
        """Save persistent alert state"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving alert state: {e}")
    
    def _is_quiet_hours(self) -> bool:
        """Check if we're in Kelly's quiet hours"""
        now = datetime.now().time()
        quiet_start = datetime.strptime(self.alert_config["quiet_hours_start"], "%H:%M").time()
        quiet_end = datetime.strptime(self.alert_config["quiet_hours_end"], "%H:%M").time()
        
        if quiet_start < quiet_end:
            return quiet_start <= now <= quiet_end
        else:  # Overnight quiet period
            return now >= quiet_start or now <= quiet_end
    
    def _is_weekend_mode(self) -> bool:
        """Check if we should use gentler weekend approach"""
        if not self.alert_config["weekend_gentler"]:
            return False
        
        weekday = datetime.now().weekday()
        return weekday >= 5  # Saturday = 5, Sunday = 6
    
    def _can_send_alert(self, urgency: str = "normal") -> Tuple[bool, str]:
        """Check if we can send an alert given current limits and timing"""
        state = self._load_alert_state()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset daily counter if new day
        if state.get("current_date") != today:
            state["alerts_sent_today"] = 0
            state["current_date"] = today
            self._save_alert_state(state)
        
        # Check quiet hours
        if self._is_quiet_hours():
            return False, "quiet_hours"
        
        # Check daily limit
        if state["alerts_sent_today"] >= self.alert_config["max_alerts_per_day"]:
            return False, "daily_limit"
        
        # Check cooldown period
        if state.get("last_alert_time"):
            last_alert = datetime.fromisoformat(state["last_alert_time"])
            cooldown = timedelta(hours=self.alert_config["cooldown_hours"])
            if datetime.now() - last_alert < cooldown:
                return False, "cooldown_active"
        
        # Weekend mode - be more selective
        if self._is_weekend_mode() and urgency == "low":
            return False, "weekend_mode"
        
        return True, "allowed"
    
    def _format_alert_for_kelly(self, message: str, urgency: str, pattern_data: Dict) -> str:
        """Format alert message in Kelly's style using existing voice system"""
        
        # Let the existing voice system handle Kelly's style
        if hasattr(self.voice, 'format_alert_message'):
            # Use voice system if it has alert formatting
            return self.voice.format_alert_message(message, urgency, pattern_data)
        
        # Otherwise format manually in Kelly's style
        kelly_formatted = []
        
        # Add gentle prefix based on urgency
        if urgency == "high":
            kelly_formatted.append("💙 Hey Kelly, your body's been sending some signals...")
        elif urgency == "moderate": 
            kelly_formatted.append("💙 Kelly, I'm noticing something worth checking in about...")
        else:
            kelly_formatted.append("💙 Just a gentle check-in...")
        
        # Add the main message (should already be in Kelly's voice from voice system)
        kelly_formatted.append(message)
        
        # Add gentle closing
        if self._is_weekend_mode():
            kelly_formatted.append("No pressure - just wanted you to know what I'm seeing. 💙")
        else:
            kelly_formatted.append("How are you feeling about that? 💙")
        
        return "\n\n".join(kelly_formatted)
    
    async def _send_whatsapp_message(self, message: str) -> bool:
        """Send message via WhatsApp using existing message system"""
        try:
            # Use the workspace message tool to send to Kelly
            cmd = [
                "python3", "-m", "openclaw.tools.message",
                "send", "--channel", "whatsapp", 
                "--target", "kelly",  # Assuming Kelly is the default target
                "--message", message
            ]
            
            result = subprocess.run(
                cmd, 
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.info("WhatsApp message sent successfully")
                return True
            else:
                self.logger.error(f"WhatsApp send failed: {result.stderr}")
                # Fall back to file method
                return await self._write_to_file(message)
                
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp message: {e}")
            # Fall back to file method
            return await self._write_to_file(message)
    
    async def _write_to_file(self, message: str) -> bool:
        """Write alert to file for Kelly to see later"""
        try:
            alert_file = self.workspace / "memory" / f"welly-alert-{datetime.now().strftime('%Y-%m-%d')}.md"
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            with open(alert_file, 'a') as f:
                f.write(f"\n## Welly Alert - {timestamp}\n\n")
                f.write(message)
                f.write("\n\n---\n")
            
            self.logger.info(f"Alert written to {alert_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing alert to file: {e}")
            return False
    
    async def _log_alert(self, message: str) -> bool:
        """Log alert to system log"""
        try:
            self.logger.info(f"WELLY ALERT: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Error logging alert: {e}")
            return False
    
    async def send_gentle_alert(self, message: str, urgency: str = "normal", pattern_data: Optional[Dict] = None) -> bool:
        """Send a gentle alert to Kelly if timing/limits allow"""
        
        # Check if we can send alert
        can_send, reason = self._can_send_alert(urgency)
        
        if not can_send:
            self.logger.info(f"Alert suppressed: {reason}")
            # Still log for debug purposes
            await self._log_alert(f"[SUPPRESSED - {reason}] {message}")
            return False
        
        # Format in Kelly's style
        formatted_message = self._format_alert_for_kelly(message, urgency, pattern_data or {})
        
        # Try to deliver via preferred method
        delivery_method = self.delivery_methods.get(
            self.alert_config["preferred_channel"], 
            self._write_to_file
        )
        
        success = await delivery_method(formatted_message)
        
        if success:
            # Update state
            state = self._load_alert_state()
            state["alerts_sent_today"] = state.get("alerts_sent_today", 0) + 1
            state["last_alert_time"] = datetime.now().isoformat()
            state["total_alerts_sent"] = state.get("total_alerts_sent", 0) + 1
            
            # Add to history
            if "alert_history" not in state:
                state["alert_history"] = []
            
            state["alert_history"].append({
                "timestamp": datetime.now().isoformat(),
                "urgency": urgency,
                "method": self.alert_config["preferred_channel"],
                "message_preview": message[:100] + "..." if len(message) > 100 else message
            })
            
            # Keep only last 20 alerts in history
            if len(state["alert_history"]) > 20:
                state["alert_history"] = state["alert_history"][-20:]
            
            self._save_alert_state(state)
            
            self.logger.info(f"Gentle alert sent successfully via {self.alert_config['preferred_channel']}")
            
        return success
    
    def get_alert_status(self) -> Dict:
        """Get current alert system status"""
        state = self._load_alert_state()
        can_send, reason = self._can_send_alert()
        
        return {
            "can_send_alert": can_send,
            "suppression_reason": reason if not can_send else None,
            "alerts_sent_today": state.get("alerts_sent_today", 0),
            "daily_limit": self.alert_config["max_alerts_per_day"],
            "total_alerts_sent": state.get("total_alerts_sent", 0),
            "last_alert_time": state.get("last_alert_time"),
            "in_quiet_hours": self._is_quiet_hours(),
            "weekend_mode": self._is_weekend_mode(),
            "preferred_channel": self.alert_config["preferred_channel"],
            "cooldown_hours": self.alert_config["cooldown_hours"]
        }
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """Get recent alert history"""
        state = self._load_alert_state()
        history = state.get("alert_history", [])
        
        return history[-count:] if history else []


def main():
    """CLI for testing alert system"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        alerts = WellyAlerts()
        
        if command == "test":
            # Test sending an alert
            import asyncio
            
            async def test_alert():
                test_message = "Your body's been whispering for a few days. This looks like one of your 'I can push through it' stretches. How are you feeling about that?"
                
                success = await alerts.send_gentle_alert(
                    test_message, 
                    urgency="moderate",
                    pattern_data={"pattern_type": "push_through", "days": 3}
                )
                
                print(f"Test alert sent: {success}")
            
            asyncio.run(test_alert())
            
        elif command == "status":
            status = alerts.get_alert_status()
            
            print("💙 Welly Alert System Status")
            print(f"   Can send alert: {status['can_send_alert']}")
            if status.get('suppression_reason'):
                print(f"   Suppressed: {status['suppression_reason']}")
            print(f"   Alerts today: {status['alerts_sent_today']}/{status['daily_limit']}")
            print(f"   Total sent: {status['total_alerts_sent']}")
            print(f"   Last alert: {status.get('last_alert_time', 'Never')}")
            print(f"   Quiet hours: {status['in_quiet_hours']}")
            print(f"   Weekend mode: {status['weekend_mode']}")
            print(f"   Channel: {status['preferred_channel']}")
            
        elif command == "history":
            history = alerts.get_recent_alerts(10)
            
            print("💙 Recent Welly Alerts")
            if not history:
                print("   No alerts sent recently")
            else:
                for alert in history:
                    timestamp = alert['timestamp']
                    urgency = alert['urgency']
                    preview = alert['message_preview']
                    print(f"   {timestamp} [{urgency}]: {preview}")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-alerts.py [test|status|history]")
    else:
        print("Welly Alerts - Smart Alerting System")
        print("Usage: python3 welly-alerts.py [test|status|history]")


if __name__ == "__main__":
    main()
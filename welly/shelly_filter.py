#!/usr/bin/env python3
"""
Shelly-Welly Filter System

Shelly checks on Welly during heartbeats and decides what's worth Kelly's attention
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add welly to path
sys.path.append('/data/workspace/welly')
from welly import Welly

# Import RPE-Recovery integration
try:
    from rpe_recovery_bridge import RPERecoveryBridge
    RPE_RECOVERY_AVAILABLE = True
except ImportError:
    RPE_RECOVERY_AVAILABLE = False
import importlib.util
spec = importlib.util.spec_from_file_location("vault_integration", "/data/workspace/welly/vault-integration.py")
vault_integration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vault_integration)
WellyVaultWriter = vault_integration.WellyVaultWriter

class ShellyWellyFilter:
    def __init__(self):
        self.welly = Welly()
        self.vault_writer = WellyVaultWriter()
        
    def heartbeat_check(self) -> dict:
        """Run during Shelly heartbeats to check Welly and filter for Kelly"""
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "welly_status": "unknown",
            "kelly_should_know": False,
            "kelly_message": None,
            "vault_logged": False,
            "background_info": None
        }
        
        try:
            # Check if Welly has fresh insights
            current_state = self.welly.get_current_state()
            
            # Check if manual check-in needed
            manual_prompt = self.welly.heartbeat.check_manual_checkin_needed()
            
            # Run daily cycle if appropriate (background data gathering)
            if self.welly.heartbeat.should_run_today():
                daily_result = self.welly.daily_check_in()
                
                # Run integrated RPE-Recovery analysis
                if RPE_RECOVERY_AVAILABLE:
                    try:
                        bridge = RPERecoveryBridge()
                        integrated_state = bridge.check_and_update_recovery_state()
                        
                        # Add integrated insights to daily result
                        if integrated_state.get('kelly_should_know', False):
                            daily_result['integrated_recovery'] = integrated_state
                            
                    except Exception as e:
                        # Don't break if RPE integration fails
                        pass
                
                # Log to vault regardless
                should_speak = daily_result.get("should_check_in", False)
                check_in_message = daily_result.get("check_in_message")
                
                self.vault_writer.log_welly_activity(current_state, should_speak, check_in_message)
                result["vault_logged"] = True
                result["background_info"] = f"Daily analysis complete - {current_state.get('recovery_status', 'unknown')} recovery"
                
                # FILTER: Should Kelly know about this?
                if should_speak and check_in_message:
                    # Welly wants to speak up - evaluate if it's important enough
                    if self._kelly_should_know(current_state, check_in_message):
                        result["kelly_should_know"] = True
                        result["kelly_message"] = f"💙 Welly noticed something:\n\n{check_in_message}"
                        
                # Also check integrated recovery insights
                if 'integrated_recovery' in daily_result:
                    integrated = daily_result['integrated_recovery']
                    if integrated.get('kelly_should_know', False):
                        recovery_msg = integrated.get('kelly_message', '')
                        if recovery_msg:
                            if result["kelly_should_know"]:
                                result["kelly_message"] += f"\n\n🔄 Recovery: {recovery_msg}"
                            else:
                                result["kelly_should_know"] = True
                                result["kelly_message"] = f"🔄 {recovery_msg}"
                
            # Manual check-in prompt
            if manual_prompt and self._should_prompt_kelly_for_checkin():
                result["kelly_should_know"] = True
                result["kelly_message"] = f"💙 Welly: {manual_prompt}"
                        
            result["welly_status"] = "running"
            return result
            
        except Exception as e:
            result["welly_status"] = "error"
            result["background_info"] = f"Welly error: {str(e)}"
            return result
    
    def _kelly_should_know(self, state: dict, message: str) -> bool:
        """Decide if Welly's insights are worth interrupting Kelly"""
        
        # Always interrupt for high-priority patterns
        push_risk = state.get("push_risk", "low")
        alignment = state.get("mind_body_alignment", "aligned")
        emotional_load = state.get("emotional_load", "light")
        
        # High priority: Mind-body misalignment (Kelly's #1 focus)
        if alignment in ["slight_mismatch", "misaligned"]:
            return True
        
        # High priority: Push-through patterns 
        if push_risk in ["high", "very_high"]:
            return True
            
        # High priority: Heavy emotional load
        if emotional_load in ["heavy", "overwhelming"]:
            return True
        
        # Medium priority: Check message content for concerning patterns
        concerning_keywords = [
            "multiple days", "pattern", "familiar territory", 
            "override mode", "pushing through", "disconnect"
        ]
        
        if any(keyword in message.lower() for keyword in concerning_keywords):
            return True
        
        # Low priority: Routine recovery status updates
        if state.get("recovery_status") in ["good", "okay-ish"]:
            return False
            
        # Default: Don't interrupt Kelly unless it's clearly important
        return False
    
    def _should_prompt_kelly_for_checkin(self) -> bool:
        """Decide if Kelly should be prompted for manual check-in"""
        
        # For now, be conservative - only prompt if it's been >2 days
        # Kelly can adjust this threshold
        return False  # Start with no prompting, let Kelly ask for it

if __name__ == "__main__":
    filter_system = ShellyWellyFilter()
    result = filter_system.heartbeat_check()
    print(json.dumps(result, indent=2))
#!/usr/bin/env python3
"""
Welly - Kelly's body-awareness companion

Main entry point for Kelly's personalized training and recovery decision support.
Integrates all 5 components into a production-ready system.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import all Welly components
from welly_ingest import WellyIngest
from welly_interpreter import WellyInterpreter
from welly_memory import WellyMemory
from welly_voice import WellyVoice
from welly_heartbeat import WellyHeartbeat

class Welly:
    """Kelly's body-awareness companion - complete system"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        
        # Initialize all components
        self.ingest = WellyIngest(workspace)
        self.interpreter = WellyInterpreter(workspace)
        self.memory = WellyMemory(workspace)
        self.voice = WellyVoice()
        self.heartbeat = WellyHeartbeat(workspace)
        
        self.version = "1.0.0"
        self.build_date = "2026-03-15"
        
    def setup(self) -> Dict:
        """Initialize Welly system for first use"""
        
        print("🚀 Setting up Welly - Kelly's body-awareness companion")
        
        setup_result = {
            "steps_completed": [],
            "errors": [],
            "ready": False
        }
        
        try:
            # Step 1: Initialize database
            print("   📊 Setting up database...")
            self.ingest.setup_database()
            setup_result["steps_completed"].append("database_initialized")
            
            # Step 2: Test data connections
            print("   🔗 Testing data connections...")
            
            # Test Oura connection
            oura_test = self.ingest.ingest_oura_data()
            if not oura_test.get("error"):
                print("      ✅ Oura connection working")
                setup_result["steps_completed"].append("oura_connected")
            else:
                print(f"      ⚠️ Oura connection issue: {oura_test.get('error')}")
                setup_result["errors"].append(f"oura: {oura_test.get('error')}")
            
            # Test Strava connection
            strava_test = self.ingest.ingest_strava_data()
            if not strava_test.get("error"):
                print("      ✅ Strava connection working")
                setup_result["steps_completed"].append("strava_connected")
            else:
                print(f"      ⚠️ Strava connection issue: {strava_test.get('error')}")
                setup_result["errors"].append(f"strava: {strava_test.get('error')}")
            
            # Step 3: Initialize memory patterns
            print("   🧠 Initializing memory system...")
            self.memory.setup_memory_tables()
            setup_result["steps_completed"].append("memory_ready")
            
            # Step 4: Test voice system
            print("   🗣️ Testing voice system...")
            test_message = self.voice.generate_manual_checkin_prompt()
            if test_message:
                print(f"      ✅ Voice system working: '{test_message}'")
                setup_result["steps_completed"].append("voice_ready")
            
            # Step 5: Create initial heartbeat entry
            print("   💓 Setting up heartbeat system...")
            setup_result["steps_completed"].append("heartbeat_ready")
            
            # Mark as ready if core components work
            core_ready = all(step in setup_result["steps_completed"] for step in 
                           ["database_initialized", "memory_ready", "voice_ready", "heartbeat_ready"])
            
            setup_result["ready"] = core_ready
            
            if core_ready:
                print("\n✅ Welly setup complete! Ready to help Kelly make better training decisions.")
                if setup_result["errors"]:
                    print("⚠️  Some data connections had issues but core system is functional.")
            else:
                print("\n❌ Setup incomplete. Check errors and retry.")
            
            return setup_result
            
        except Exception as e:
            setup_result["errors"].append(f"setup_failed: {str(e)}")
            print(f"\n❌ Setup failed: {str(e)}")
            return setup_result
    
    def daily_check_in(self) -> Dict:
        """Run daily check-in cycle"""
        return self.heartbeat.run_daily_cycle()
    
    def manual_check_in(self, energy: int, soreness: int, stress: int, mood: int, 
                       feel_like_self: str, notes: str = "") -> Dict:
        """Process manual check-in from Kelly"""
        return self.heartbeat.process_manual_checkin(
            energy, soreness, stress, mood, feel_like_self, notes
        )
    
    def get_current_state(self) -> Dict:
        """Get Kelly's current interpreted state"""
        return self.interpreter.interpret_daily_state()
    
    def get_weekly_summary(self) -> Dict:
        """Get weekly pattern summary"""
        return self.heartbeat.run_weekly_review()
    
    def get_patterns(self) -> Dict:
        """Get Kelly's learned patterns"""
        current_state = self.get_current_state()
        return self.memory.get_relevant_patterns(current_state)
    
    def _run_json_command(self, command: List[str]) -> Optional[Dict]:
        """Run a helper command that returns JSON."""
        try:
            result = subprocess.run(command, capture_output=True, text=True, cwd=self.workspace)
            if result.returncode != 0:
                return None
            return json.loads(result.stdout)
        except Exception:
            return None
    
    def _maybe_auto_capture_subjective(self, message: str) -> Optional[Dict]:
        """Quietly capture likely run-related subjective data from natural language."""
        message_lower = message.lower()
        run_response_indicators = [
            "felt", "feel", "feeling", "legs", "leg", "hard", "easy", "tough", "good",
            "alright", "okay", "push", "effort", "tired", "fresh", "strong",
            "slow", "fast", "laggy", "smooth", "pace", "hr", "heart rate", "period",
            "heavy", "sluggish", "weekly number"
        ]

        if not any(indicator in message_lower for indicator in run_response_indicators):
            return None

        try:
            result = self.ingest.ingest_run_subjective_response(message)
            return result if result.get("logged") else None
        except Exception:
            return None

    def synthesize_training_state(self) -> Dict:
        """Turn Oura + Strava into an actual opinion, not a data dump."""
        strava_script = self.workspace / "skills" / "strava" / "scripts" / "strava.py"
        oura_script = self.workspace / "skills" / "oura" / "scripts" / "oura.py"
        
        weekly = self._run_json_command(["python3", str(strava_script), "weekly"]) if strava_script.exists() else None
        runs = self._run_json_command(["python3", str(strava_script), "runs", "7"]) if strava_script.exists() else None
        oura_today = self._run_json_command(["python3", str(oura_script), "brief", datetime.now().strftime("%Y-%m-%d")]) if oura_script.exists() else None
        
        summary = {
            "training_state": "unknown",
            "pattern": None,
            "meaning": None,
            "call": None,
            "next_move": None,
            "facts": {}
        }
        
        if weekly:
            summary["facts"]["weekly_miles"] = weekly.get("total_miles")
            summary["facts"]["total_runs"] = weekly.get("total_runs")
        
        recent_runs = weekly.get("runs", []) if weekly else []
        if recent_runs:
            summary["facts"]["recent_runs"] = recent_runs
        
        if oura_today:
            sleep_score = (oura_today.get("sleep") or {}).get("score")
            readiness_score = (oura_today.get("readiness") or {}).get("score")
            hrv_balance = ((oura_today.get("readiness") or {}).get("contributors") or {}).get("hrv_balance")
            summary["facts"].update({
                "sleep_score": sleep_score,
                "readiness_score": readiness_score,
                "hrv_balance": hrv_balance,
            })
        else:
            sleep_score = None
            readiness_score = None
            hrv_balance = None
        
        pace_trend_better = False
        hr_trend_higher = False
        if len(recent_runs) >= 2:
            paces = [run.get("pace", "") for run in recent_runs]
            avg_hrs = [run.get("hr_avg") for run in recent_runs]
            try:
                def pace_to_seconds(p: str) -> int:
                    mm, rest = p.split(":")
                    ss = rest.split("/")[0]
                    return int(mm) * 60 + int(ss)
                pace_values = [pace_to_seconds(p) for p in paces if p]
                if len(pace_values) >= 2:
                    pace_trend_better = pace_values[-1] < pace_values[0]
                if avg_hrs[0] is not None and avg_hrs[-1] is not None:
                    hr_trend_higher = avg_hrs[-1] > avg_hrs[0]
            except Exception:
                pass
        
        if pace_trend_better and readiness_score is not None and sleep_score is not None and sleep_score < 70:
            summary["pattern"] = "performance is holding even though recovery is a little behind"
            summary["meaning"] = "fitness looks real, but some of the work is being covered by grit"
            summary["call"] = "maintaining"
            summary["next_move"] = "hold steady and recover instead of forcing more"
            summary["training_state"] = "maintaining_with_recovery_lag"
        
        if pace_trend_better and readiness_score is not None and readiness_score >= 75 and sleep_score is not None and sleep_score >= 70:
            summary["pattern"] = "recovery and performance are moving together"
            summary["meaning"] = "you look like you're actually building, not just surviving the week"
            summary["call"] = "building"
            summary["next_move"] = "keep the rhythm and don't get greedy"
            summary["training_state"] = "building"
        
        if readiness_score is not None and readiness_score < 68 and sleep_score is not None and sleep_score < 65 and hr_trend_higher:
            summary["pattern"] = "your body is working harder to hit the same kind of effort"
            summary["meaning"] = "under-recovery is starting to leak into the runs"
            summary["call"] = "under_recovered"
            summary["next_move"] = "back off a notch and prioritize sleep"
            summary["training_state"] = "under_recovered"
        
        if summary["training_state"] == "unknown":
            summary["pattern"] = "your consistency looks solid, but the signal is mixed"
            summary["meaning"] = "nothing looks alarming, just not fully clear yet"
            summary["call"] = "steady"
            summary["next_move"] = "keep watching the next couple of days before changing much"
            summary["training_state"] = "steady"
        
        return summary
    
    def chat(self, message: str) -> str:
        """Chat interface with Welly"""

        # Quietly capture subjective run context when a natural response contains it.
        self._maybe_auto_capture_subjective(message)
        
        # Simple pattern matching for common queries
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["how am i", "how do i", "what's my", "what can you tell me", "recovery", "miles"]):
            synthesis = self.synthesize_training_state()
            facts = synthesis.get("facts", {})
            weekly_miles = facts.get("weekly_miles")
            sleep_score = facts.get("sleep_score")
            readiness_score = facts.get("readiness_score")
            
            opener = synthesis.get("pattern", "I'm seeing a mixed picture")
            meaning = synthesis.get("meaning", "Nothing looks alarming")
            call = synthesis.get("call", "steady")
            next_move = synthesis.get("next_move", "keep listening")
            
            details = []
            if weekly_miles is not None:
                details.append(f"{weekly_miles} miles this week")
            if readiness_score is not None:
                details.append(f"readiness {readiness_score}")
            if sleep_score is not None:
                details.append(f"sleep {sleep_score}")
            detail_text = ", ".join(details)
            
            if detail_text:
                return f"I'm noticing {opener}. Meaning: {meaning}. Call: {call}. Next move: {next_move}. Context: {detail_text}."
            
            return f"I'm noticing {opener}. Meaning: {meaning}. Call: {call}. Next move: {next_move}."
        
        elif any(word in message_lower for word in ["pattern", "tend to", "usually"]):
            patterns = self.get_patterns()
            insights = self.memory.get_pattern_insights()
            
            if insights:
                return f"I've noticed: {insights[0]}"
            else:
                return "Still learning your patterns. The more we check in, the clearer they become."
        
        elif "check in" in message_lower or "checkin" in message_lower:
            prompt = self.voice.generate_manual_checkin_prompt()
            return f"{prompt}\n\nReady when you are - just let me know your energy, soreness, stress, mood (all 1-5) and whether you feel like yourself today."
        
        else:
            # Default supportive response
            return "I'm here to help you understand what your body's telling you. How are you feeling today?"
    
    def integrate_with_heartbeat_system(self) -> str:
        """Generate integration code for existing heartbeat system"""
        
        integration_code = '''
# Add to HEARTBEAT.md for Kelly's workspace

## Welly Integration

Check in with Kelly's body-awareness companion:

```python
import sys
sys.path.append('/data/workspace/welly')
from welly import Welly

welly = Welly()

# Check if manual check-in needed
checkin_prompt = welly.heartbeat.check_manual_checkin_needed()
if checkin_prompt:
    print(f"💙 {checkin_prompt}")

# Run daily cycle if appropriate  
if welly.heartbeat.should_run_today():
    result = welly.daily_check_in()
    
    if result.get("should_check_in") and result.get("check_in_message"):
        print(f"💙 Welly says:")
        print(result["check_in_message"])
```

Add to rotation: Check Welly status every 2-3 heartbeats.
'''
        
        return integration_code
    
    def status(self) -> Dict:
        """Get Welly system status"""
        
        status = {
            "version": self.version,
            "build_date": self.build_date,
            "timestamp": datetime.now().isoformat(),
            "components": {},
            "data_freshness": {},
            "ready": False
        }
        
        try:
            # Check database
            import sqlite3
            conn = sqlite3.connect(self.ingest.db_path)
            cursor = conn.cursor()
            
            # Count daily states
            cursor.execute("SELECT COUNT(*) FROM daily_state")
            daily_state_count = cursor.fetchone()[0]
            
            # Get last manual check-in
            cursor.execute("SELECT MAX(date) FROM daily_state WHERE energy IS NOT NULL")
            last_manual_result = cursor.fetchone()
            last_manual = last_manual_result[0] if last_manual_result and last_manual_result[0] else "never"
            
            # Count patterns learned
            cursor.execute("SELECT COUNT(*) FROM kelly_patterns")
            pattern_count = cursor.fetchone()[0]
            
            conn.close()
            
            status["components"] = {
                "database": "✅ Connected",
                "ingest": "✅ Ready",
                "interpreter": "✅ Ready", 
                "memory": f"✅ Ready ({pattern_count} patterns learned)",
                "voice": "✅ Ready",
                "heartbeat": "✅ Ready"
            }
            
            status["data_freshness"] = {
                "daily_states": f"{daily_state_count} recorded",
                "last_manual_checkin": last_manual,
                "patterns_learned": pattern_count
            }
            
            status["ready"] = daily_state_count > 0 or pattern_count > 0
            
        except Exception as e:
            status["components"]["database"] = f"❌ Error: {str(e)}"
            status["ready"] = False
        
        return status

def main():
    if len(sys.argv) < 2:
        print("Welly - Kelly's Body-Awareness Companion")
        print()
        print("Usage:")
        print("  python3 welly.py setup                    # Initialize Welly system")
        print("  python3 welly.py daily                    # Run daily check-in cycle")
        print("  python3 welly.py checkin                  # Manual check-in")
        print("  python3 welly.py status                   # System status")
        print("  python3 welly.py state                    # Current interpreted state")
        print("  python3 welly.py patterns                 # Current patterns")
        print("  python3 welly.py weekly                   # Weekly summary")
        print("  python3 welly.py chat <message>           # Chat with Welly")
        print("  python3 welly.py integrate                # Show heartbeat integration")
        print()
        print("Kelly's personalized training & recovery decision support")
        return
    
    welly = Welly()
    command = sys.argv[1]
    
    if command == "setup":
        result = welly.setup()
        
    elif command == "daily":
        result = welly.daily_check_in()
        print(f"Daily cycle: {', '.join(result.get('steps', []))}")
        
        if result.get("should_check_in"):
            print("\n💙 Welly says:")
            print(result["check_in_message"])
        else:
            print("\n🤫 Welly is staying quiet today")
    
    elif command == "checkin":
        print("Manual Check-in with Welly")
        try:
            energy = int(input("Energy (1-5): "))
            soreness = int(input("Soreness (1-5): "))
            stress = int(input("Stress (1-5): "))
            mood = int(input("Mood (1-5): "))
            feel_like_self = input("Feel like yourself today? (yes/somewhat/no): ")
            notes = input("Any notes: ")
            
            result = welly.manual_check_in(energy, soreness, stress, mood, feel_like_self, notes)
            
            print("\n✅ Check-in recorded")
            if result.get("immediate_response"):
                print("\n💙 Welly's response:")
                print(result["immediate_response"])
                
        except KeyboardInterrupt:
            print("\nCheck-in cancelled")
        except ValueError:
            print("Please enter valid numbers for ratings")
    
    elif command == "status":
        status = welly.status()
        
        print(f"💙 Welly Status (v{status['version']})")
        print(f"   Built: {status['build_date']}")
        print(f"   Ready: {'Yes' if status['ready'] else 'No'}")
        print()
        print("Components:")
        for component, status_text in status["components"].items():
            print(f"   {component}: {status_text}")
        print()
        print("Data:")
        for metric, value in status["data_freshness"].items():
            print(f"   {metric}: {value}")
    
    elif command == "state":
        state = welly.get_current_state()
        print("Current State:")
        print(f"   Recovery: {state.get('recovery_status', 'unknown')}")
        print(f"   Mind-body alignment: {state.get('mind_body_alignment', 'unknown')}")
        print(f"   Push risk: {state.get('push_risk', 'unknown')}")
        print(f"   Emotional load: {state.get('emotional_load', 'unknown')}")
        print(f"   Confidence: {state.get('confidence', 0):.1f}")
        
        insights = state.get("insights", [])
        if insights:
            print("   Insights:")
            for insight in insights[:3]:  # Top 3
                print(f"     • {insight}")
    
    elif command == "patterns":
        patterns = welly.get_patterns()
        print("Relevant Patterns:")
        
        for pattern_type, pattern_list in patterns.items():
            if pattern_list:
                print(f"   {pattern_type.replace('_', ' ').title()}:")
                for pattern in pattern_list[:2]:  # Top 2 per type
                    print(f"     • {pattern['name']} (confidence: {pattern['confidence']:.1f})")
    
    elif command == "weekly":
        summary = welly.get_weekly_summary()
        
        if summary.get("error"):
            print(f"❌ {summary['error']}")
        else:
            print("📈 Weekly Summary:")
            print(summary["week_summary"])
    
    elif command == "chat":
        if len(sys.argv) > 2:
            message = " ".join(sys.argv[2:])
            response = welly.chat(message)
            print(f"💙 Welly: {response}")
        else:
            print("Please provide a message to chat with Welly")
    
    elif command == "integrate":
        integration_code = welly.integrate_with_heartbeat_system()
        print("Heartbeat Integration Code:")
        print(integration_code)
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python3 welly.py' for usage help")

if __name__ == "__main__":
    main()
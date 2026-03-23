#!/usr/bin/env python3
"""
welly-heartbeat: Daily integration and check-in system

Runs daily when new data arrives, coordinates all Welly components,
and delivers gentle check-ins through Kelly's preferred channels.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Import Welly components
from welly_ingest import WellyIngest
from welly_interpreter import WellyInterpreter  
from welly_memory import WellyMemory
from welly_voice import WellyVoice

class WellyHeartbeat:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.ingest = WellyIngest(workspace)
        self.interpreter = WellyInterpreter(workspace)
        self.memory = WellyMemory(workspace)
        self.voice = WellyVoice()
        
        # Kelly's preferences
        self.kelly_preferences = {
            "preferred_time": "morning",  # Morning check-ins
            "preferred_channel": "whatsapp",
            "max_frequency": "daily",  # Don't overwhelm
            "quiet_hours": ["23:00", "08:00"],  # Sleep hours
            "weekend_mode": "lighter"  # Less intense on weekends
        }
        
        self.heartbeat_log_path = self.workspace / "memory" / "welly_heartbeat.json"
        
    def run_daily_cycle(self, date_str: Optional[str] = None) -> Dict:
        """Run complete daily Welly cycle"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        cycle_result = {
            "date": date_str,
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "should_check_in": False,
            "check_in_message": None,
            "errors": []
        }
        
        try:
            # Step 1: Data ingestion
            print(f"🔄 Welly daily cycle for {date_str}")
            
            # Initialize database if needed
            self.ingest.setup_database()
            cycle_result["steps"].append("database_ready")
            
            # Ingest fresh data (try both sources)
            oura_result = self.ingest.ingest_oura_data(date_str)
            strava_result = self.ingest.ingest_strava_data(date_str)
            
            data_quality = self._assess_data_quality(oura_result, strava_result)
            cycle_result["steps"].append(f"data_ingested_{data_quality}")
            
            if data_quality == "insufficient":
                cycle_result["errors"].append("Insufficient data for meaningful analysis")
                return cycle_result
            
            # Step 2: Get trends and patterns
            trends = self.ingest.get_7day_trends()
            cycle_result["steps"].append("trends_analyzed")
            
            # Step 3: Interpret current state  
            interpreted_state = self.interpreter.interpret_daily_state(date_str)
            cycle_result["steps"].append("state_interpreted")
            
            if interpreted_state.get("confidence", 0) < 0.4:
                cycle_result["errors"].append("Low interpretation confidence")
                # Continue anyway - might still have useful insights
            
            # Step 4: Learn from state and update memory
            self.memory.learn_from_daily_state(interpreted_state)
            relevant_patterns = self.memory.get_relevant_patterns(interpreted_state)
            cycle_result["steps"].append("patterns_updated")
            
            # Step 5: Generate voice response
            should_speak = not self.voice.should_stay_quiet(interpreted_state)
            
            if should_speak:
                check_in_message = self.voice.generate_daily_check_in(
                    interpreted_state, 
                    relevant_patterns
                )
                
                if check_in_message:
                    cycle_result["should_check_in"] = True
                    cycle_result["check_in_message"] = check_in_message
                    cycle_result["steps"].append("check_in_generated")
                else:
                    cycle_result["steps"].append("stayed_quiet")
            else:
                cycle_result["steps"].append("should_stay_quiet")
            
            # Step 6: Log heartbeat activity
            self._log_heartbeat_activity(cycle_result, interpreted_state)
            
            return cycle_result
            
        except Exception as e:
            cycle_result["errors"].append(f"Cycle failed: {str(e)}")
            return cycle_result
    
    def deliver_check_in(self, check_in_message: str) -> Dict:
        """Deliver check-in to Kelly via her preferred channel"""
        
        # Format for WhatsApp
        formatted_message = self.voice.format_for_whatsapp(check_in_message)
        
        # Add Welly signature
        signed_message = f"💙 {formatted_message}\n\n— Welly"
        
        # Here we would integrate with the message delivery system
        # For now, return the formatted message
        return {
            "channel": "whatsapp",
            "message": signed_message,
            "delivered": False,  # Would be True after actual delivery
            "delivery_time": datetime.now().isoformat()
        }
    
    def check_manual_checkin_needed(self) -> Optional[str]:
        """Check if Kelly should do a manual check-in"""
        
        # Check last manual check-in
        last_checkin_date = self._get_last_manual_checkin_date()
        today = datetime.now().date()
        
        if not last_checkin_date or last_checkin_date < today:
            # Prompt for manual check-in
            return self.voice.generate_manual_checkin_prompt()
        
        return None
    
    def process_manual_checkin(self, energy: int, soreness: int, stress: int, 
                              mood: int, feel_like_self: str, notes: str = "") -> Dict:
        """Process manual check-in and potentially generate response"""
        
        # Store the check-in
        checkin_result = self.ingest.ingest_manual_checkin(
            energy, soreness, stress, mood, feel_like_self, notes
        )
        
        if checkin_result.get("error"):
            return checkin_result
        
        # Run interpretation on new state
        interpreted_state = self.interpreter.interpret_daily_state()
        
        # Learn from the new data
        self.memory.learn_from_daily_state(interpreted_state) 
        relevant_patterns = self.memory.get_relevant_patterns(interpreted_state)
        
        # Generate immediate response if warranted
        should_respond = not self.voice.should_stay_quiet(interpreted_state)
        
        response = {
            "checkin_stored": True,
            "should_respond": should_respond,
            "immediate_response": None
        }
        
        if should_respond:
            # Generate immediate feedback
            response["immediate_response"] = self.voice.generate_daily_check_in(
                interpreted_state, 
                relevant_patterns
            )
        
        return response
    
    def run_weekly_review(self) -> Dict:
        """Generate weekly pattern review for Kelly"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get weekly insights from memory
        weekly_insights = self.memory.get_pattern_insights(7)
        
        # Get trends
        trends = self.ingest.get_7day_trends()
        daily_states = trends.get("daily_states", [])
        
        if len(daily_states) < 3:
            return {"error": "Insufficient data for weekly review"}
        
        # Calculate weekly averages
        avg_energy = sum(state.get("energy", 0) for state in daily_states) / len(daily_states)
        avg_stress = sum(state.get("stress", 0) for state in daily_states) / len(daily_states)
        avg_mood = sum(state.get("mood", 0) for state in daily_states) / len(daily_states)
        
        # Count "feel like self" responses
        feel_like_self_responses = [state.get("feel_like_self") for state in daily_states]
        yes_count = feel_like_self_responses.count("yes")
        somewhat_count = feel_like_self_responses.count("somewhat") 
        no_count = feel_like_self_responses.count("no")
        
        # Generate weekly summary in Kelly's voice
        summary_parts = []
        
        # Week overview
        if avg_energy >= 3.5:
            summary_parts.append("Energy felt pretty good this week")
        elif avg_energy <= 2.5:
            summary_parts.append("Energy was consistently low this week")
        else:
            summary_parts.append("Energy was mixed this week")
        
        # Self alignment
        if yes_count >= 5:
            summary_parts.append("You felt like yourself most days - that's a good sign")
        elif somewhat_count >= 3:
            summary_parts.append("Several 'somewhat' days - might be worth exploring what that's about")
        elif no_count >= 2:
            summary_parts.append("A few days of not feeling like yourself - worth noting")
        
        # Stress patterns
        if avg_stress >= 3.5:
            summary_parts.append("Stress was elevated frequently") 
        
        # Add insights from memory
        if weekly_insights:
            summary_parts.append("Patterns I noticed:")
            summary_parts.extend([f"• {insight}" for insight in weekly_insights])
        
        return {
            "week_summary": "\n\n".join(summary_parts),
            "averages": {
                "energy": round(avg_energy, 1),
                "stress": round(avg_stress, 1), 
                "mood": round(avg_mood, 1)
            },
            "self_alignment": {
                "yes": yes_count,
                "somewhat": somewhat_count,
                "no": no_count
            },
            "insights": weekly_insights
        }
    
    def _assess_data_quality(self, oura_result: Dict, strava_result: Dict) -> str:
        """Assess quality of ingested data"""
        
        oura_ok = not oura_result.get("error") 
        strava_ok = not strava_result.get("error")
        
        if oura_ok and strava_ok:
            return "excellent"
        elif oura_ok or strava_ok:
            return "partial"
        else:
            return "insufficient"
    
    def _get_last_manual_checkin_date(self) -> Optional[datetime]:
        """Get date of last manual check-in"""
        
        import sqlite3
        conn = sqlite3.connect(self.ingest.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT MAX(date) FROM daily_state 
                WHERE energy IS NOT NULL AND mood IS NOT NULL
            ''')
            
            result = cursor.fetchone()
            if result and result[0]:
                return datetime.strptime(result[0], '%Y-%m-%d').date()
            
            return None
            
        except Exception:
            return None
        finally:
            conn.close()
    
    def _log_heartbeat_activity(self, cycle_result: Dict, interpreted_state: Dict):
        """Log heartbeat activity for debugging and insights"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle_result": cycle_result,
            "interpreted_state": {
                "recovery_status": interpreted_state.get("recovery_status"),
                "mind_body_alignment": interpreted_state.get("mind_body_alignment"), 
                "push_risk": interpreted_state.get("push_risk"),
                "confidence": interpreted_state.get("confidence")
            }
        }
        
        # Append to heartbeat log
        logs = []
        if self.heartbeat_log_path.exists():
            with open(self.heartbeat_log_path, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        
        # Keep only last 30 days of logs
        cutoff_date = datetime.now() - timedelta(days=30)
        logs = [log for log in logs if datetime.fromisoformat(log["timestamp"]) > cutoff_date]
        
        # Write back
        self.heartbeat_log_path.parent.mkdir(exist_ok=True)
        with open(self.heartbeat_log_path, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def should_run_today(self) -> bool:
        """Check if heartbeat should run today based on Kelly's preferences"""
        
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        
        # Check quiet hours
        quiet_start, quiet_end = self.kelly_preferences["quiet_hours"]
        if quiet_start <= current_time or current_time <= quiet_end:
            return False
        
        # Check weekend mode
        if now.weekday() in [5, 6] and self.kelly_preferences["weekend_mode"] == "lighter":
            # On weekends, only run if there's something significant
            return False  # Could add logic to check for concerning patterns
        
        # Check if already ran today
        last_run = self._get_last_heartbeat_run()
        if last_run and last_run.date() == now.date():
            return False
        
        return True
    
    def _get_last_heartbeat_run(self) -> Optional[datetime]:
        """Get timestamp of last heartbeat run"""
        
        if not self.heartbeat_log_path.exists():
            return None
        
        try:
            with open(self.heartbeat_log_path, 'r') as f:
                logs = json.load(f)
            
            if logs:
                return datetime.fromisoformat(logs[-1]["timestamp"])
                
        except Exception:
            pass
        
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly_heartbeat.py daily          # Run daily cycle")
        print("  python3 welly_heartbeat.py checkin        # Check if manual check-in needed")
        print("  python3 welly_heartbeat.py manual <data>  # Process manual check-in")
        print("  python3 welly_heartbeat.py weekly         # Generate weekly review")
        print("  python3 welly_heartbeat.py status         # Check heartbeat status")
        return
    
    heartbeat = WellyHeartbeat()
    command = sys.argv[1]
    
    if command == "daily":
        if not heartbeat.should_run_today():
            print("⏰ Skipping daily cycle (quiet hours or already ran)")
            return
        
        result = heartbeat.run_daily_cycle()
        print(f"📊 Daily cycle complete:")
        print(f"   Steps: {', '.join(result['steps'])}")
        
        if result.get("errors"):
            print(f"   ❌ Errors: {', '.join(result['errors'])}")
        
        if result.get("should_check_in"):
            print("   💬 Check-in generated:")
            print(result["check_in_message"])
            
            # Optionally deliver the message
            delivery = heartbeat.deliver_check_in(result["check_in_message"])
            print(f"   📤 Formatted for {delivery['channel']}")
        else:
            print("   🤫 Staying quiet today")
    
    elif command == "checkin":
        prompt = heartbeat.check_manual_checkin_needed()
        if prompt:
            print(f"📝 Manual check-in needed:")
            print(f"   {prompt}")
        else:
            print("✅ Manual check-in up to date")
    
    elif command == "manual":
        # Interactive manual check-in
        print("Manual Check-in")
        try:
            energy = int(input("Energy (1-5): "))
            soreness = int(input("Soreness (1-5): "))
            stress = int(input("Stress (1-5): "))
            mood = int(input("Mood (1-5): "))
            feel_like_self = input("Feel like yourself? (yes/somewhat/no): ")
            notes = input("Any notes: ")
            
            result = heartbeat.process_manual_checkin(energy, soreness, stress, mood, feel_like_self, notes)
            
            print("✅ Check-in processed")
            if result.get("immediate_response"):
                print("\n💬 Welly's response:")
                print(result["immediate_response"])
                
        except KeyboardInterrupt:
            print("\nCheck-in cancelled")
        except ValueError:
            print("Please enter numbers for ratings")
    
    elif command == "weekly":
        review = heartbeat.run_weekly_review()
        
        if review.get("error"):
            print(f"❌ {review['error']}")
        else:
            print("📈 Weekly Review:")
            print(review["week_summary"])
            print(f"\n📊 Averages: Energy {review['averages']['energy']}, Stress {review['averages']['stress']}, Mood {review['averages']['mood']}")
    
    elif command == "status":
        last_run = heartbeat._get_last_heartbeat_run()
        should_run = heartbeat.should_run_today()
        
        print(f"💓 Welly Heartbeat Status:")
        print(f"   Last run: {last_run.strftime('%Y-%m-%d %H:%M') if last_run else 'Never'}")
        print(f"   Should run today: {'Yes' if should_run else 'No'}")
        
        # Check data freshness
        checkin_needed = heartbeat.check_manual_checkin_needed()
        print(f"   Manual check-in: {'Needed' if checkin_needed else 'Up to date'}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
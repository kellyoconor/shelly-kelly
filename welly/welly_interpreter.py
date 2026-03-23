#!/usr/bin/env python3
"""
welly-interpreter: Convert raw data into Kelly's recovery insights

Transforms Oura/Strava data into recovery state, load trends, and mind/body 
mismatch signals using Kelly's specific patterns and preferences.
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class WellyInterpreter:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        
        # Kelly's specific interpretation thresholds
        self.kelly_baselines = {
            "sleep_hours_good": 7.5,
            "sleep_hours_minimum": 6.5,
            "readiness_good": 75,
            "readiness_concerning": 60,
            "hrv_drop_threshold": 15,  # % drop from baseline
            "resting_hr_elevation": 8,  # bpm above baseline
            "energy_threshold": 3,      # 1-5 scale
            "motivation_threshold": 3,  # 1-5 scale
            "stress_high": 4,           # 1-5 scale
        }
        
    def interpret_daily_state(self, date_str: Optional[str] = None) -> Dict:
        """Interpret current state from all available data"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's data
        daily_data = self._get_daily_data(date_str)
        trends = self._get_recent_trends(date_str, 7)
        
        interpretation = {
            "date": date_str,
            "recovery_status": "unknown",
            "mind_body_alignment": "unknown", 
            "push_risk": "unknown",
            "emotional_load": "unknown",
            "insights": [],
            "patterns": [],
            "confidence": 0.0
        }
        
        # Analyze recovery status
        recovery_analysis = self._analyze_recovery(daily_data, trends)
        interpretation["recovery_status"] = recovery_analysis["status"]
        interpretation["insights"].extend(recovery_analysis["insights"])
        
        # Analyze mind-body alignment (Kelly's key focus)
        alignment_analysis = self._analyze_mind_body_alignment(daily_data, trends)
        interpretation["mind_body_alignment"] = alignment_analysis["status"]
        interpretation["insights"].extend(alignment_analysis["insights"])
        
        # Analyze push risk (Kelly's tendency to push through)
        risk_analysis = self._analyze_push_risk(daily_data, trends)
        interpretation["push_risk"] = risk_analysis["level"]
        interpretation["insights"].extend(risk_analysis["insights"])
        
        # Analyze emotional load
        emotional_analysis = self._analyze_emotional_load(daily_data, trends)
        interpretation["emotional_load"] = emotional_analysis["level"]
        interpretation["insights"].extend(emotional_analysis["insights"])
        
        # Check for patterns Kelly should know about
        patterns = self._identify_patterns(trends)
        interpretation["patterns"] = patterns
        
        # Calculate interpretation confidence
        interpretation["confidence"] = self._calculate_confidence(daily_data)
        
        return interpretation
    
    def _analyze_recovery(self, daily_data: Dict, trends: Dict) -> Dict:
        """Analyze recovery status from objective metrics"""
        insights = []
        
        # Sleep analysis
        sleep_quality = daily_data.get("sleep_quality")
        sleep_hours = daily_data.get("oura", {}).get("sleep", {}).get("total_hours", 0)
        
        if sleep_hours < self.kelly_baselines["sleep_hours_minimum"]:
            insights.append(f"Sleep debt building: {sleep_hours:.1f}h last night")
        
        # Readiness analysis
        readiness = daily_data.get("readiness")
        if readiness and readiness < self.kelly_baselines["readiness_concerning"]:
            insights.append(f"Body readiness low: {readiness}")
        
        # HRV trend analysis
        hrv_trend = self._analyze_hrv_trend(trends.get("oura_trends", []))
        if hrv_trend["drop_percentage"] > self.kelly_baselines["hrv_drop_threshold"]:
            insights.append(f"HRV down {hrv_trend['drop_percentage']:.0f}% from baseline")
        
        # Determine overall recovery status
        if len(insights) == 0:
            status = "good"
        elif len(insights) <= 1:
            status = "okay-ish" 
        elif len(insights) <= 2:
            status = "concerning"
        else:
            status = "needs-attention"
        
        return {
            "status": status,
            "insights": insights
        }
    
    def _analyze_mind_body_alignment(self, daily_data: Dict, trends: Dict) -> Dict:
        """Analyze whether what Kelly feels matches what she's doing - KEY FOCUS"""
        insights = []
        
        # Get subjective data
        energy = daily_data.get("energy")
        mood = daily_data.get("mood") 
        feel_like_self = daily_data.get("feel_like_self")
        
        # Get objective data
        readiness = daily_data.get("readiness")
        workout_load = daily_data.get("workout_load", 0) or 0
        
        # Check for mismatches
        mismatches = []
        
        # Body says not ready, but energy feels good
        if readiness and readiness < 65 and energy and energy >= 4:
            mismatches.append("Energy feels good but body metrics suggest rest")
            
        # Body says ready, but energy feels low
        if readiness and readiness > 75 and energy and energy <= 2:
            mismatches.append("Numbers look good but energy feels low")
        
        # High workout load with low subjective scores
        if workout_load and workout_load > 7 and energy and energy <= 2:
            mismatches.append("High training load but energy tanking")
        
        # Feel like self misalignment  
        if feel_like_self == "no" and readiness and readiness > 70:
            mismatches.append("Metrics okay but don't feel like yourself")
            
        if feel_like_self == "yes" and readiness and readiness < 60:
            mismatches.append("Feel good but body metrics concerning")
        
        # Determine alignment status
        if len(mismatches) == 0:
            status = "aligned"
            insights.append("Mind and body seem in sync")
        elif len(mismatches) == 1:
            status = "slight_mismatch"
            insights.extend(mismatches)
        else:
            status = "misaligned"
            insights.extend(mismatches)
            insights.append("Worth checking in with yourself")
        
        return {
            "status": status,
            "insights": insights
        }
    
    def _analyze_push_risk(self, daily_data: Dict, trends: Dict) -> Dict:
        """Analyze Kelly's tendency to push through when she shouldn't"""
        insights = []
        
        # Get stress and motivation levels
        stress = daily_data.get("stress", 3)
        motivation = daily_data.get("motivation", 3)
        energy = daily_data.get("energy", 3)
        
        # Check recent pattern of pushing
        recent_states = trends.get("daily_states", [])
        push_indicators = 0
        
        # High stress + high motivation = classic push pattern
        if stress >= 4 and motivation >= 4:
            push_indicators += 1
            insights.append("High stress but high motivation - classic push zone")
        
        # Low energy but high workout loads recently
        recent_workout_loads = [state.get("workout_load", 0) for state in recent_states[-3:]]
        if energy <= 2 and any(load > 6 for load in recent_workout_loads):
            push_indicators += 1
            insights.append("Low energy but maintained high training loads")
        
        # Pattern of "somewhat" feeling like self
        feel_like_self_answers = [state.get("feel_like_self") for state in recent_states[-3:]]
        if feel_like_self_answers.count("somewhat") >= 2:
            push_indicators += 1
            insights.append("Been feeling 'somewhat' like yourself - might be pushing")
        
        # Readiness declining but maintaining efforts
        readiness_trend = self._get_readiness_trend(trends.get("oura_trends", []))
        if readiness_trend["declining"] and daily_data.get("workout_load", 0) > 5:
            push_indicators += 1
            insights.append("Readiness trending down but training intensity up")
        
        # Determine push risk level
        if push_indicators == 0:
            level = "low"
        elif push_indicators <= 1:
            level = "moderate"
        elif push_indicators <= 2: 
            level = "high"
        else:
            level = "very_high"
            insights.append("Multiple push-through patterns detected")
        
        return {
            "level": level,
            "insights": insights
        }
    
    def _analyze_emotional_load(self, daily_data: Dict, trends: Dict) -> Dict:
        """Analyze emotional state impact on recovery"""
        insights = []
        
        stress = daily_data.get("stress", 3)
        mood = daily_data.get("mood", 3) 
        feel_like_self = daily_data.get("feel_like_self", "yes")
        
        emotional_score = 0
        
        if stress >= 4:
            emotional_score += 2
            insights.append(f"Stress elevated: {stress}/5")
        
        if mood <= 2:
            emotional_score += 2
            insights.append(f"Mood low: {mood}/5")
        
        if feel_like_self == "no":
            emotional_score += 2
            insights.append("Not feeling like yourself")
        elif feel_like_self == "somewhat":
            emotional_score += 1
            insights.append("Only somewhat feeling like yourself")
        
        # Check for emotional patterns in trends
        recent_stress = [state.get("stress", 3) for state in trends.get("daily_states", [])[-3:]]
        if recent_stress and len(recent_stress) > 0 and sum(recent_stress) / len(recent_stress) > 3.5:
            emotional_score += 1
            insights.append("Stress elevated multiple days")
        
        # Determine emotional load level
        if emotional_score == 0:
            level = "light"
        elif emotional_score <= 2:
            level = "moderate" 
        elif emotional_score <= 4:
            level = "heavy"
        else:
            level = "overwhelming"
        
        return {
            "level": level,
            "insights": insights
        }
    
    def _identify_patterns(self, trends: Dict) -> List[str]:
        """Identify recurring patterns Kelly should be aware of"""
        patterns = []
        
        daily_states = trends.get("daily_states", [])
        if len(daily_states) < 3:
            return patterns
        
        # Check for pattern: Monday blues
        monday_energies = []
        for state in daily_states:
            if state.get("date"):
                date_obj = datetime.strptime(state["date"], "%Y-%m-%d")
                if date_obj.weekday() == 0:  # Monday
                    monday_energies.append(state.get("energy", 3))
        
        if monday_energies and sum(monday_energies) / len(monday_energies) < 2.5:
            patterns.append("Monday energy consistently low")
        
        # Check for weekend recovery pattern
        weekend_readiness = []
        for state in daily_states:
            if state.get("date"):
                date_obj = datetime.strptime(state["date"], "%Y-%m-%d")
                if date_obj.weekday() in [5, 6]:  # Sat/Sun
                    weekend_readiness.append(state.get("readiness", 70))
        
        if weekend_readiness and sum(weekend_readiness) / len(weekend_readiness) > 75:
            patterns.append("Weekends good for recovery")
        
        # Check for stress-training correlation
        stress_workout_pairs = []
        for state in daily_states:
            if state.get("stress") and state.get("workout_load"):
                stress_workout_pairs.append((state["stress"], state["workout_load"]))
        
        if len(stress_workout_pairs) >= 3:
            high_stress_high_load = sum(1 for s, w in stress_workout_pairs if s >= 4 and w >= 6)
            if high_stress_high_load >= 2:
                patterns.append("Tends to maintain high training when stressed")
        
        return patterns
    
    def _analyze_hrv_trend(self, oura_trends: List[Dict]) -> Dict:
        """Analyze HRV trend over recent days"""
        if len(oura_trends) < 3:
            return {"drop_percentage": 0, "trend": "insufficient_data"}
        
        hrv_values = []
        for day_data in oura_trends:
            readiness_data = day_data.get("readiness_data", {})
            if readiness_data and "hrv" in readiness_data:
                hrv_values.append(readiness_data["hrv"])
        
        if len(hrv_values) < 3:
            return {"drop_percentage": 0, "trend": "insufficient_data"}
        
        baseline = sum(hrv_values[:-3]) / len(hrv_values[:-3]) if len(hrv_values) > 3 else hrv_values[0]
        recent = sum(hrv_values[-3:]) / 3
        
        drop_percentage = ((baseline - recent) / baseline * 100) if baseline > 0 else 0
        
        return {
            "drop_percentage": drop_percentage,
            "baseline": baseline,
            "recent": recent,
            "trend": "declining" if drop_percentage > 5 else "stable"
        }
    
    def _get_readiness_trend(self, oura_trends: List[Dict]) -> Dict:
        """Get readiness trend direction"""
        if len(oura_trends) < 3:
            return {"declining": False, "trend": "insufficient_data"}
        
        readiness_values = []
        for day_data in oura_trends[-5:]:  # Last 5 days
            readiness_data = day_data.get("readiness_data", {})
            if readiness_data and "score" in readiness_data:
                readiness_values.append(readiness_data["score"])
        
        if len(readiness_values) < 3:
            return {"declining": False, "trend": "insufficient_data"}
        
        # Simple trend: are last 2 days lower than previous 3?
        early_avg = sum(readiness_values[:-2]) / len(readiness_values[:-2])
        recent_avg = sum(readiness_values[-2:]) / 2
        
        declining = recent_avg < early_avg - 5  # 5 point threshold
        
        return {
            "declining": declining,
            "early_avg": early_avg,
            "recent_avg": recent_avg,
            "trend": "declining" if declining else "stable"
        }
    
    def _get_daily_data(self, date_str: str) -> Dict:
        """Get all data for a specific date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get daily state
            cursor.execute('''
                SELECT * FROM daily_state WHERE date = ?
            ''', (date_str,))
            
            state_row = cursor.fetchone()
            if not state_row:
                return {}
            
            # Convert to dict (matching table columns)
            daily_data = {
                "date": state_row[0],
                "sleep_quality": state_row[1],
                "readiness": state_row[2], 
                "hrv_rmssd": state_row[3],
                "resting_hr": state_row[4],
                "workout_load": state_row[5],
                "soreness": state_row[6],
                "energy": state_row[7],
                "motivation": state_row[8],
                "stress": state_row[9],
                "mood": state_row[10],
                "feel_like_self": state_row[11],
                "notes": state_row[12]
            }
            
            # Get Oura data
            cursor.execute('''
                SELECT sleep_data, readiness_data FROM oura_data WHERE date = ?
            ''', (date_str,))
            
            oura_row = cursor.fetchone()
            if oura_row:
                daily_data["oura"] = {
                    "sleep": json.loads(oura_row[0]) if oura_row[0] else {},
                    "readiness": json.loads(oura_row[1]) if oura_row[1] else {}
                }
            
            return daily_data
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def _get_recent_trends(self, end_date: str, days_back: int) -> Dict:
        """Get trend data for recent period"""
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        start_dt = end_dt - timedelta(days=days_back)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get daily states
            cursor.execute('''
                SELECT date, energy, soreness, stress, mood, feel_like_self, workout_load, readiness
                FROM daily_state 
                WHERE date >= ? AND date <= ?
                ORDER BY date
            ''', (start_dt.strftime('%Y-%m-%d'), end_date))
            
            daily_states = []
            for row in cursor.fetchall():
                daily_states.append({
                    "date": row[0],
                    "energy": row[1],
                    "soreness": row[2],
                    "stress": row[3], 
                    "mood": row[4],
                    "feel_like_self": row[5],
                    "workout_load": row[6],
                    "readiness": row[7]
                })
            
            # Get Oura trends
            cursor.execute('''
                SELECT date, readiness_data, sleep_data
                FROM oura_data
                WHERE date >= ? AND date <= ?
                ORDER BY date
            ''', (start_dt.strftime('%Y-%m-%d'), end_date))
            
            oura_trends = []
            for row in cursor.fetchall():
                oura_trends.append({
                    "date": row[0],
                    "readiness_data": json.loads(row[1]) if row[1] else {},
                    "sleep_data": json.loads(row[2]) if row[2] else {}
                })
            
            return {
                "daily_states": daily_states,
                "oura_trends": oura_trends
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()
    
    def _calculate_confidence(self, daily_data: Dict) -> float:
        """Calculate confidence in interpretation based on data completeness"""
        data_points = 0
        total_possible = 8
        
        if daily_data.get("energy"): data_points += 1
        if daily_data.get("mood"): data_points += 1  
        if daily_data.get("stress"): data_points += 1
        if daily_data.get("feel_like_self"): data_points += 1
        if daily_data.get("readiness"): data_points += 1
        if daily_data.get("hrv_rmssd"): data_points += 1
        if daily_data.get("sleep_quality"): data_points += 1
        if daily_data.get("workout_load"): data_points += 1
        
        return data_points / total_possible

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly_interpreter.py interpret [date]   # Interpret daily state")
        print("  python3 welly_interpreter.py patterns [days]    # Identify patterns")
        return
    
    interpreter = WellyInterpreter()
    command = sys.argv[1]
    
    if command == "interpret":
        date_str = sys.argv[2] if len(sys.argv) > 2 else None
        result = interpreter.interpret_daily_state(date_str)
        print(json.dumps(result, indent=2))
        
    elif command == "patterns":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        trends = interpreter._get_recent_trends(datetime.now().strftime('%Y-%m-%d'), days)
        patterns = interpreter._identify_patterns(trends)
        print("Patterns identified:")
        for pattern in patterns:
            print(f"  • {pattern}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
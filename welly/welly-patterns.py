#!/usr/bin/env python3
"""
Welly Patterns - Real-Time Pattern Detection Engine

Analyzes Kelly's body-mind patterns in real-time, building on existing
memory system to detect concerning trends that warrant gentle attention.

Preserves all existing pattern learning while adding always-on detection.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import existing Welly components
from welly_memory import WellyMemory
from welly_interpreter import WellyInterpreter

class WellyPatterns:
    """Real-time pattern detection that enhances existing memory system"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        
        # Use existing Welly components
        self.memory = WellyMemory(workspace)
        self.interpreter = WellyInterpreter(workspace)
        
        # Pattern detection thresholds (Kelly-specific)
        self.thresholds = {
            "push_pattern": {
                "days_declining_readiness": 3,  # 3+ days declining readiness
                "high_effort_on_low_readiness": 2,  # 2+ days high effort when readiness low
                "override_body_signals": 2  # Pushing when body says no
            },
            "recovery_pattern": {
                "consistent_good_recovery": 5,  # 5+ days of good recovery
                "alignment_streak": 4,  # 4+ days mind-body aligned  
                "positive_trend_days": 7  # Week of positive trends
            },
            "warning_pattern": {
                "mind_body_misalignment_days": 3,  # 3+ days misaligned
                "low_energy_streak": 4,  # 4+ days low energy
                "stress_plus_effort": 2,  # High stress + high effort combo
                "ignore_fatigue_pattern": 2  # Kelly pushing through fatigue signals
            }
        }
        
        self.logger = logging.getLogger(__name__)
        
    def _get_recent_states(self, days: int = 7) -> List[Dict]:
        """Get recent daily states for pattern analysis"""
        try:
            conn = sqlite3.connect(self.memory.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            cursor.execute('''
                SELECT * FROM daily_state 
                WHERE date BETWEEN ? AND ?
                ORDER BY date DESC
            ''', (start_date, end_date))
            
            states = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return states
            
        except Exception as e:
            self.logger.error(f"Error getting recent states: {e}")
            return []
    
    def _detect_push_through_pattern(self, states: List[Dict]) -> Optional[Dict]:
        """Detect Kelly's tendency to push through declining signals"""
        if len(states) < 3:
            return None
        
        pattern_signals = []
        consecutive_decline = 0
        high_effort_on_low_readiness = 0
        
        for i, state in enumerate(states):
            readiness = state.get('readiness_score', 100)
            effort_level = self._estimate_effort_level(state)
            mind_body_alignment = state.get('mind_body_alignment', 'aligned')
            
            # Check for declining readiness pattern
            if i > 0:
                prev_readiness = states[i-1].get('readiness_score', 100)
                if readiness < prev_readiness:
                    consecutive_decline += 1
                else:
                    consecutive_decline = 0
            
            # Check for high effort on low readiness (Kelly's classic pattern)
            if readiness < 70 and effort_level > 3:  # Low readiness but pushing hard
                high_effort_on_low_readiness += 1
                pattern_signals.append(f"Day {i+1}: High effort ({effort_level}) with low readiness ({readiness})")
            
            # Check for mind-body misalignment while pushing
            if mind_body_alignment == 'misaligned' and effort_level > 3:
                pattern_signals.append(f"Day {i+1}: Pushing through body signals")
        
        # Determine if this is Kelly's concerning push pattern
        if (consecutive_decline >= self.thresholds["push_pattern"]["days_declining_readiness"] or
            high_effort_on_low_readiness >= self.thresholds["push_pattern"]["high_effort_on_low_readiness"]):
            
            return {
                "pattern_type": "push_through",
                "severity": "concerning" if high_effort_on_low_readiness >= 3 else "warning",
                "description": "Stacking effort on declining readiness",
                "kelly_specific": True,  # This is Kelly's known pattern
                "signals": pattern_signals,
                "days_detected": max(consecutive_decline, high_effort_on_low_readiness),
                "message_suggestion": "You've been stacking effort on declining readiness for a few days"
            }
        
        return None
    
    def _detect_positive_alignment_pattern(self, states: List[Dict]) -> Optional[Dict]:
        """Detect when Kelly's in a good recovery/alignment streak"""
        if len(states) < 4:
            return None
        
        alignment_days = 0
        recovery_days = 0
        pattern_signals = []
        
        for i, state in enumerate(states):
            alignment = state.get('mind_body_alignment', 'aligned')
            recovery_status = state.get('recovery_status', 'okay-ish')
            readiness = state.get('readiness_score', 100)
            
            if alignment == 'aligned':
                alignment_days += 1
            
            if recovery_status in ['good', 'excellent']:
                recovery_days += 1
                
            if readiness > 75 and alignment == 'aligned':
                pattern_signals.append(f"Day {i+1}: Good alignment and readiness ({readiness})")
        
        # Kelly's doing well - positive reinforcement opportunity
        if (alignment_days >= self.thresholds["recovery_pattern"]["alignment_streak"] and
            recovery_days >= 3):
            
            return {
                "pattern_type": "positive_alignment", 
                "severity": "positive",
                "description": "Solid recovery and body-mind alignment",
                "kelly_specific": True,
                "signals": pattern_signals,
                "days_detected": min(alignment_days, recovery_days),
                "message_suggestion": "Your recovery has been solid this week, body's responding well"
            }
        
        return None
    
    def _detect_early_warning_pattern(self, states: List[Dict]) -> Optional[Dict]:
        """Detect early warning signs before Kelly hits a wall"""
        if len(states) < 3:
            return None
        
        warning_signals = []
        misalignment_days = 0
        stress_effort_combo = 0
        energy_declining = True
        
        prev_energy = None
        for i, state in enumerate(states):
            energy = state.get('energy', 3)
            stress = state.get('stress', 3) 
            alignment = state.get('mind_body_alignment', 'aligned')
            effort_level = self._estimate_effort_level(state)
            
            # Track mind-body misalignment
            if alignment in ['misaligned', 'slight_mismatch']:
                misalignment_days += 1
            
            # Track stress + high effort combination (Kelly red flag)
            if stress >= 4 and effort_level >= 4:
                stress_effort_combo += 1
                warning_signals.append(f"Day {i+1}: High stress ({stress}) + high effort ({effort_level})")
            
            # Track energy trend
            if prev_energy and energy >= prev_energy:
                energy_declining = False
            prev_energy = energy
        
        # Early warning patterns
        if (misalignment_days >= self.thresholds["warning_pattern"]["mind_body_misalignment_days"] or
            stress_effort_combo >= self.thresholds["warning_pattern"]["stress_plus_effort"]):
            
            severity = "early_warning"
            if stress_effort_combo >= 3:  # Very concerning
                severity = "concerning"
            
            return {
                "pattern_type": "early_warning",
                "severity": severity,
                "description": "Early warning signs of potential burnout pattern",
                "kelly_specific": True,
                "signals": warning_signals,
                "days_detected": max(misalignment_days, stress_effort_combo),
                "message_suggestion": "I'm seeing some early signals your body's trying to tell you something"
            }
        
        return None
    
    def _estimate_effort_level(self, state: Dict) -> int:
        """Estimate effort level from available data (1-5 scale)"""
        # This would integrate with Strava workout intensity, Oura activity data, etc.
        # For now, use basic heuristics
        
        activity_score = state.get('activity_score', 3)
        workout_intensity = state.get('workout_intensity', 3)
        subjective_effort = state.get('perceived_effort', 3)
        
        # Use whatever data is available
        if subjective_effort:
            return subjective_effort
        elif workout_intensity:
            return workout_intensity
        elif activity_score:
            return min(5, int(activity_score / 20))  # Convert 0-100 to 1-5
        else:
            return 3  # Default moderate
    
    def _detect_kelly_specific_patterns(self, states: List[Dict]) -> List[Dict]:
        """Detect patterns specific to Kelly's tendencies"""
        patterns = []
        
        # Kelly's main patterns from memory
        push_pattern = self._detect_push_through_pattern(states)
        if push_pattern:
            patterns.append(push_pattern)
        
        positive_pattern = self._detect_positive_alignment_pattern(states)  
        if positive_pattern:
            patterns.append(positive_pattern)
        
        warning_pattern = self._detect_early_warning_pattern(states)
        if warning_pattern:
            patterns.append(warning_pattern)
        
        return patterns
    
    async def analyze_concerning_patterns(self, current_state: Dict) -> Dict:
        """Main pattern analysis - detect concerning trends for alerts"""
        analysis = {
            "concerning_patterns": [],
            "positive_patterns": [],
            "urgency": "normal",
            "alert_worthy": False,
            "confidence": 0.0
        }
        
        try:
            # Get recent states for pattern analysis
            recent_states = self._get_recent_states(7)
            
            if len(recent_states) < 2:
                analysis["confidence"] = 0.0
                return analysis
            
            # Detect Kelly-specific patterns
            patterns = self._detect_kelly_specific_patterns(recent_states)
            
            for pattern in patterns:
                if pattern["severity"] in ["concerning", "warning"]:
                    analysis["concerning_patterns"].append(pattern)
                    analysis["alert_worthy"] = True
                    
                    if pattern["severity"] == "concerning":
                        analysis["urgency"] = "high"
                    elif analysis["urgency"] == "normal":
                        analysis["urgency"] = "moderate"
                        
                elif pattern["severity"] == "positive":
                    analysis["positive_patterns"].append(pattern)
            
            # Use existing memory system to enhance pattern detection
            memory_patterns = self.memory.get_relevant_patterns(current_state)
            
            # Cross-reference with learned patterns
            for pattern_type, pattern_list in memory_patterns.items():
                for learned_pattern in pattern_list:
                    if learned_pattern.get("confidence", 0) > 0.7:
                        # High-confidence learned pattern matches current situation
                        if any(concern in learned_pattern.get("name", "").lower() 
                              for concern in ["push", "override", "ignore", "fatigue"]):
                            analysis["alert_worthy"] = True
                            if analysis["urgency"] == "normal":
                                analysis["urgency"] = "moderate"
            
            # Calculate overall confidence
            if recent_states:
                analysis["confidence"] = min(1.0, len(recent_states) / 7.0)  # More confidence with more data
            
        except Exception as e:
            self.logger.error(f"Error analyzing patterns: {e}")
            analysis["error"] = str(e)
        
        return analysis
    
    def get_pattern_summary(self, days: int = 14) -> Dict:
        """Get summary of recent patterns for manual review"""
        try:
            states = self._get_recent_states(days)
            patterns = self._detect_kelly_specific_patterns(states)
            
            summary = {
                "timeframe_days": days,
                "states_analyzed": len(states),
                "patterns_detected": len(patterns),
                "pattern_breakdown": {
                    "concerning": [],
                    "warning": [],
                    "positive": []
                },
                "overall_trend": "neutral"
            }
            
            for pattern in patterns:
                severity = pattern["severity"]
                if severity in ["concerning", "warning"]:
                    summary["pattern_breakdown"][severity].append(pattern)
                elif severity == "positive":
                    summary["pattern_breakdown"]["positive"].append(pattern)
            
            # Determine overall trend
            if summary["pattern_breakdown"]["concerning"]:
                summary["overall_trend"] = "concerning"
            elif summary["pattern_breakdown"]["warning"]:
                summary["overall_trend"] = "warning"
            elif summary["pattern_breakdown"]["positive"]:
                summary["overall_trend"] = "positive"
            
            return summary
            
        except Exception as e:
            return {"error": str(e)}


def main():
    """CLI for testing pattern detection"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        patterns = WellyPatterns()
        
        if command == "analyze":
            # Analyze current patterns
            import asyncio
            
            async def analyze_current():
                # Get current state from interpreter
                interpreter = WellyInterpreter()
                current_state = interpreter.interpret_daily_state()
                
                analysis = await patterns.analyze_concerning_patterns(current_state)
                
                print("🔍 Current Pattern Analysis")
                print(f"   Alert worthy: {analysis['alert_worthy']}")
                print(f"   Urgency: {analysis['urgency']}")
                print(f"   Confidence: {analysis['confidence']:.2f}")
                
                if analysis["concerning_patterns"]:
                    print("   Concerning patterns:")
                    for pattern in analysis["concerning_patterns"]:
                        print(f"     • {pattern['description']}")
                
                if analysis["positive_patterns"]:
                    print("   Positive patterns:")
                    for pattern in analysis["positive_patterns"]:
                        print(f"     • {pattern['description']}")
            
            asyncio.run(analyze_current())
            
        elif command == "summary":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 14
            summary = patterns.get_pattern_summary(days)
            
            print(f"📈 Pattern Summary ({days} days)")
            print(f"   States analyzed: {summary['states_analyzed']}")
            print(f"   Patterns detected: {summary['patterns_detected']}")
            print(f"   Overall trend: {summary['overall_trend']}")
            
            for severity, pattern_list in summary["pattern_breakdown"].items():
                if pattern_list:
                    print(f"   {severity.capitalize()} patterns:")
                    for pattern in pattern_list:
                        print(f"     • {pattern['description']} ({pattern['days_detected']} days)")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-patterns.py [analyze|summary [days]]")
    else:
        print("Welly Patterns - Real-Time Pattern Detection")
        print("Usage: python3 welly-patterns.py [analyze|summary [days]]")


if __name__ == "__main__":
    main()
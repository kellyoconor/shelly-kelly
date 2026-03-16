#!/usr/bin/env python3
"""
Intelligence Layer Builder - Turn Kelly's data into insights

This builds the missing 20%: pattern recognition algorithms that synthesize
captured data into actionable insights.
"""

import os
import json
import glob
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any

class KellyIntelligence:
    """Core intelligence algorithms for pattern recognition"""
    
    def __init__(self):
        self.vault_path = "/data/kelly-vault"
        self.workspace_memory = "/data/workspace/memory"
        self.daily_notes_path = f"{self.vault_path}/Daily Notes"
        
    def analyze_health_decision_correlation(self, days_back=14):
        """Correlate Oura readiness scores with decision quality"""
        print("🔬 Analyzing health vs decision patterns...")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        health_data = []
        decision_data = []
        
        # Parse daily notes for health and decision data
        for daily_file in glob.glob(f"{self.daily_notes_path}/*.md"):
            try:
                filename = os.path.basename(daily_file)
                date_match = re.match(r"(\d{4}-\d{2}-\d{2})\.md", filename)
                if not date_match:
                    continue
                    
                file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if file_date < cutoff_date:
                    continue
                
                with open(daily_file, 'r') as f:
                    content = f.read()
                
                # Extract health indicators
                health_indicators = self._extract_health_data(content, file_date)
                if health_indicators:
                    health_data.append(health_indicators)
                
                # Extract decision mentions
                decisions = self._extract_decisions(content, file_date)
                decision_data.extend(decisions)
                    
            except Exception as e:
                print(f"Error parsing {daily_file}: {e}")
                continue
        
        # Correlate patterns
        if not health_data or not decision_data:
            return {
                "insight": f"Insufficient data for correlation (health: {len(health_data)}, decisions: {len(decision_data)})",
                "confidence": 0.0
            }
        
        # Simple correlation analysis
        correlation_insight = self._correlate_health_decisions(health_data, decision_data)
        return correlation_insight
        
    def detect_running_patterns(self, days_back=30):
        """Analyze running patterns vs life context"""
        print("🏃‍♀️ Detecting running pattern insights...")
        
        # TODO: Parse for:
        # - Strava data from daily notes
        # - Emotional states when running
        # - Running as stress response vs training
        # - Performance vs readiness correlation
        
        return {"insight": "Running patterns analysis needs implementation", "confidence": 0.0}
        
    def research_life_integration(self, days_back=7):
        """Connect research discoveries to current life themes"""
        print("🔗 Analyzing research → life connections...")
        
        # TODO: 
        # - Parse research agent outputs
        # - Connect to current decisions/projects
        # - Identify emerging themes
        
        return {"insight": "Research integration needs development", "confidence": 0.0}
        
    def calendar_energy_analysis(self, days_back=21):
        """Understand scheduling impact on energy/wellbeing"""
        print("📅 Analyzing calendar vs energy patterns...")
        
        # TODO:
        # - Parse calendar events from daily notes
        # - Correlate with readiness/mood data
        # - Identify optimal/draining schedule patterns
        
        return {"insight": "Calendar analysis needs implementation", "confidence": 0.0}
        
    def synthesize_weekly_insights(self):
        """Generate high-level insights from all patterns"""
        print("✨ Synthesizing cross-pattern insights...")
        
        insights = []
        
        # Run all analysis
        health_decision = self.analyze_health_decision_correlation()
        running = self.detect_running_patterns()
        research = self.research_life_integration()
        calendar = self.calendar_energy_analysis()
        
        # Add real insights
        if health_decision["confidence"] > 0.0:
            insights.append({
                "type": "health-decisions",
                "insight": health_decision["insight"],
                "confidence": health_decision["confidence"],
                "source": "health vs decision correlation analysis"
            })
        
        if running["confidence"] > 0.0:
            insights.append({
                "type": "running-patterns",
                "insight": running["insight"], 
                "confidence": running["confidence"],
                "source": "running pattern analysis"
            })
        
        # Meta insight about system status
        algorithms_implemented = sum(1 for result in [health_decision, running, research, calendar] if result["confidence"] > 0.0)
        insights.append({
            "type": "system",
            "insight": f"Intelligence algorithms: {algorithms_implemented}/4 operational. Health-decision correlation analysis active.",
            "confidence": 0.8,
            "next_steps": [
                "Implement running pattern analysis",
                "Build research integration algorithms", 
                "Add calendar energy correlation",
                "Connect insights to morning briefings"
            ]
        })
        
        return insights
    
    def _extract_health_data(self, content: str, date: datetime) -> Dict[str, Any]:
        """Extract health indicators from daily note content"""
        health_data = {"date": date}
        
        # Look for common health indicators
        patterns = {
            "readiness": r"readiness[:\s]*(\d+)%?",
            "sleep": r"sleep[:\s]*(\d+\.?\d*)\s*h",
            "hrv": r"hrv[:\s]*(\d+)",
            "resting_hr": r"resting[:\s]*hr[:\s]*(\d+)",
            "energy": r"energy[:\s]*(low|medium|high|tired|exhausted|energized)",
            "mood": r"mood[:\s]*(good|bad|stressed|calm|frustrated|happy)"
        }
        
        for metric, pattern in patterns.items():
            matches = re.findall(pattern, content.lower())
            if matches:
                if metric in ["energy", "mood"]:
                    health_data[metric] = matches[-1]  # Take last mention
                else:
                    try:
                        health_data[metric] = float(matches[-1])
                    except ValueError:
                        continue
        
        return health_data if len(health_data) > 1 else None
    
    def _extract_decisions(self, content: str, date: datetime) -> List[Dict[str, Any]]:
        """Extract decision mentions from daily note content"""
        decisions = []
        
        decision_patterns = [
            r"decided to (.+?)[\.\n]",
            r"chose to (.+?)[\.\n]", 
            r"going to (.+?)[\.\n]",
            r"will (.+?)[\.\n]",
            r"committed to (.+?)[\.\n]"
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, content.lower(), re.IGNORECASE)
            for match in matches:
                # Basic decision quality indicators
                decision_text = match.strip()
                quality_score = self._score_decision_quality(decision_text)
                
                decisions.append({
                    "date": date,
                    "text": decision_text,
                    "quality_score": quality_score
                })
        
        return decisions
    
    def _score_decision_quality(self, decision_text: str) -> float:
        """Basic heuristic scoring of decision quality"""
        # Positive indicators
        positive_words = ["exercise", "run", "sleep", "plan", "organize", "commit", "focus", "choose brave"]
        # Negative indicators  
        negative_words = ["procrastinate", "avoid", "cancel", "postpone", "stress", "overwhelm"]
        
        text_lower = decision_text.lower()
        
        score = 0.5  # Neutral baseline
        for word in positive_words:
            if word in text_lower:
                score += 0.2
        for word in negative_words:
            if word in text_lower:
                score -= 0.2
                
        return max(0.0, min(1.0, score))  # Clamp to 0-1
    
    def _correlate_health_decisions(self, health_data: List[Dict], decision_data: List[Dict]) -> Dict[str, Any]:
        """Find correlations between health metrics and decision quality"""
        
        # Group decisions by date
        decisions_by_date = {}
        for decision in decision_data:
            date_key = decision["date"].strftime("%Y-%m-%d")
            if date_key not in decisions_by_date:
                decisions_by_date[date_key] = []
            decisions_by_date[date_key].append(decision["quality_score"])
        
        # Calculate average decision quality per day
        daily_decision_quality = {}
        for date_key, scores in decisions_by_date.items():
            daily_decision_quality[date_key] = sum(scores) / len(scores)
        
        # Correlate with health data
        correlations = []
        for health_point in health_data:
            date_key = health_point["date"].strftime("%Y-%m-%d")
            if date_key in daily_decision_quality:
                decision_quality = daily_decision_quality[date_key]
                
                # Check each health metric
                for metric, value in health_point.items():
                    if metric != "date" and isinstance(value, (int, float)):
                        correlations.append({
                            "date": date_key,
                            "health_metric": metric,
                            "health_value": value,
                            "decision_quality": decision_quality
                        })
        
        if not correlations:
            return {"insight": "No overlapping health and decision data found", "confidence": 0.0}
        
        # Simple pattern detection
        insight = self._generate_correlation_insight(correlations)
        return insight
    
    def _generate_correlation_insight(self, correlations: List[Dict]) -> Dict[str, Any]:
        """Generate insight from correlation data"""
        if len(correlations) < 3:
            return {
                "insight": f"Insufficient data points for correlation analysis ({len(correlations)} days)",
                "confidence": 0.2
            }
        
        # Find strongest patterns
        patterns = []
        
        # Group by health metric
        by_metric = {}
        for corr in correlations:
            metric = corr["health_metric"]
            if metric not in by_metric:
                by_metric[metric] = []
            by_metric[metric].append(corr)
        
        for metric, data in by_metric.items():
            if len(data) < 3:
                continue
                
            # Simple trend analysis
            high_health = [d for d in data if d["health_value"] > 80]  # Above 80 for readiness
            low_health = [d for d in data if d["health_value"] < 60]   # Below 60
            
            if high_health and low_health:
                high_decisions = sum(d["decision_quality"] for d in high_health) / len(high_health)
                low_decisions = sum(d["decision_quality"] for d in low_health) / len(low_health)
                
                diff = high_decisions - low_decisions
                if abs(diff) > 0.1:  # Meaningful difference
                    direction = "better" if diff > 0 else "worse"
                    patterns.append(f"Higher {metric} correlates with {direction} decisions (+{diff:.1f})")
        
        if patterns:
            return {
                "insight": f"Health-decision correlation detected: {'; '.join(patterns)}",
                "confidence": min(0.8, len(correlations) / 10),  # Higher confidence with more data
                "data_points": len(correlations),
                "patterns": patterns
            }
        else:
            return {
                "insight": "No clear health-decision correlations found in recent data",
                "confidence": 0.4,
                "data_points": len(correlations)
            }

def main():
    """Run intelligence analysis"""
    intel = KellyIntelligence()
    
    print("🧠 Kelly Intelligence Layer - Pattern Recognition")
    print("=" * 50)
    
    insights = intel.synthesize_weekly_insights()
    
    print(f"\n✨ Generated {len(insights)} insights:")
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight['type'].upper()}: {insight['insight']}")
        print(f"   Confidence: {insight['confidence']:.0%}")
        
        if 'next_steps' in insight:
            print("   Next steps:")
            for step in insight['next_steps']:
                print(f"   • {step}")
    
    return 0

if __name__ == "__main__":
    exit(main())
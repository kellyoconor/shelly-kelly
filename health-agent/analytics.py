#!/usr/bin/env python3
"""
Analytics Engine for Kelly's Health Correlations Agent.
Finds patterns and correlations between sleep, recovery, and performance.
"""

import statistics
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from data_collector import HealthDataCollector
from config import HealthConfig, MIN_DATA_POINTS, CORRELATION_THRESHOLD

class HealthAnalytics:
    """Analyzes patterns in health and performance data."""
    
    def __init__(self):
        self.collector = HealthDataCollector()
        self.insights = []
    
    def calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        try:
            # Calculate means
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(y_values)
            
            # Calculate correlation components
            numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
            
            x_variance = sum((x - x_mean) ** 2 for x in x_values)
            y_variance = sum((y - y_mean) ** 2 for y in y_values)
            
            denominator = (x_variance * y_variance) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            return numerator / denominator
            
        except Exception as e:
            print(f"Correlation calculation error: {e}")
            return 0.0
    
    def analyze_sleep_pace_correlation(self, data: List[Dict]) -> Dict:
        """Analyze correlation between sleep hours and running pace."""
        sleep_hours = []
        pace_values = []
        
        for day_data in data:
            oura = day_data.get("oura")
            runs = day_data.get("strava_runs", [])
            
            if oura and runs:
                sleep_score = oura.get("sleep", {}).get("score")
                if sleep_score:
                    # Estimate sleep hours from score (rough conversion)
                    estimated_hours = 6 + (sleep_score / 100) * 3  # 6-9 hour range
                    
                    for run in runs:
                        pace = run.get("pace_min_per_mile", 0)
                        if pace > 0 and pace < 15:  # Reasonable pace range
                            sleep_hours.append(estimated_hours)
                            pace_values.append(pace)
        
        if len(sleep_hours) < MIN_DATA_POINTS:
            return {"insufficient_data": True, "data_points": len(sleep_hours)}
        
        correlation = self.calculate_correlation(sleep_hours, pace_values)
        
        # Calculate averages by sleep quality
        good_sleep_paces = [pace for hours, pace in zip(sleep_hours, pace_values) if hours >= 7.5]
        poor_sleep_paces = [pace for hours, pace in zip(sleep_hours, pace_values) if hours < 7]
        
        analysis = {
            "correlation": correlation,
            "data_points": len(sleep_hours),
            "avg_pace_good_sleep": statistics.mean(good_sleep_paces) if good_sleep_paces else None,
            "avg_pace_poor_sleep": statistics.mean(poor_sleep_paces) if poor_sleep_paces else None,
            "sleep_pace_pairs": list(zip(sleep_hours, pace_values))
        }
        
        return analysis
    
    def analyze_readiness_performance(self, data: List[Dict]) -> Dict:
        """Analyze correlation between readiness score and running performance."""
        readiness_scores = []
        pace_values = []
        
        for day_data in data:
            oura = day_data.get("oura")
            runs = day_data.get("strava_runs", [])
            
            if oura and runs:
                readiness = oura.get("readiness", {}).get("score")
                if readiness:
                    for run in runs:
                        pace = run.get("pace_min_per_mile", 0)
                        if pace > 0 and pace < 15:
                            readiness_scores.append(readiness)
                            pace_values.append(pace)
        
        if len(readiness_scores) < MIN_DATA_POINTS:
            return {"insufficient_data": True, "data_points": len(readiness_scores)}
        
        correlation = self.calculate_correlation(readiness_scores, pace_values)
        
        # Categorize by readiness bands
        excellent_paces = [pace for score, pace in zip(readiness_scores, pace_values) if score >= 85]
        good_paces = [pace for score, pace in zip(readiness_scores, pace_values) if 70 <= score < 85]
        fair_paces = [pace for score, pace in zip(readiness_scores, pace_values) if 55 <= score < 70]
        poor_paces = [pace for score, pace in zip(readiness_scores, pace_values) if score < 55]
        
        analysis = {
            "correlation": correlation,
            "data_points": len(readiness_scores),
            "avg_pace_excellent": statistics.mean(excellent_paces) if excellent_paces else None,
            "avg_pace_good": statistics.mean(good_paces) if good_paces else None,
            "avg_pace_fair": statistics.mean(fair_paces) if fair_paces else None,
            "avg_pace_poor": statistics.mean(poor_paces) if poor_paces else None
        }
        
        return analysis
    
    def find_optimal_conditions(self, data: List[Dict]) -> Dict:
        """Find conditions that lead to best running performance."""
        best_runs = []
        
        for day_data in data:
            oura = day_data.get("oura")
            runs = day_data.get("strava_runs", [])
            
            if oura and runs:
                for run in runs:
                    pace = run.get("pace_min_per_mile", 0)
                    if pace > 0 and pace < 15:
                        run_analysis = {
                            "date": day_data.get("date"),
                            "pace": pace,
                            "distance": run.get("distance_miles", 0),
                            "sleep_score": oura.get("sleep", {}).get("score"),
                            "readiness_score": oura.get("readiness", {}).get("score"),
                            "hrv_balance": oura.get("readiness", {}).get("hrv_balance"),
                            "sleep_efficiency": oura.get("sleep", {}).get("efficiency"),
                            "temperature_deviation": oura.get("readiness", {}).get("temperature_deviation", 0)
                        }
                        best_runs.append(run_analysis)

        # Sort by pace (faster = better)
        best_runs.sort(key=lambda x: x["pace"])
        
        if len(best_runs) < MIN_DATA_POINTS:
            return {"insufficient_data": True, "data_points": len(best_runs)}
        
        # Analyze top 25% of runs
        top_quarter = best_runs[:len(best_runs)//4 + 1]
        
        optimal_conditions = {
            "sample_size": len(top_quarter),
            "avg_pace": statistics.mean([run["pace"] for run in top_quarter]),
            "avg_sleep_score": statistics.mean([run["sleep_score"] for run in top_quarter if run["sleep_score"]]),
            "avg_readiness_score": statistics.mean([run["readiness_score"] for run in top_quarter if run["readiness_score"]]),
            "avg_hrv_balance": statistics.mean([run["hrv_balance"] for run in top_quarter if run["hrv_balance"]]),
            "conditions": top_quarter
        }
        
        return optimal_conditions
    
    def generate_insights(self, days_back: int = 30) -> List[Dict]:
        """Generate insights from recent data."""
        start_date, end_date = HealthConfig.get_date_range(days_back)
        data = self.collector.get_data_range(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        
        insights = []
        
        # Sleep-pace correlation
        sleep_pace = self.analyze_sleep_pace_correlation(data)
        if not sleep_pace.get("insufficient_data"):
            correlation = sleep_pace.get("correlation", 0)
            if abs(correlation) > CORRELATION_THRESHOLD:
                direction = "negative" if correlation < 0 else "positive"
                insights.append({
                    "type": "sleep_pace_correlation",
                    "correlation": correlation,
                    "direction": direction,
                    "strength": "strong" if abs(correlation) > 0.6 else "moderate",
                    "message": f"Sleep quality shows {direction} correlation with pace (r={correlation:.2f})"
                })
        
        # Readiness-performance correlation
        readiness_perf = self.analyze_readiness_performance(data)
        if not readiness_perf.get("insufficient_data"):
            insights.append({
                "type": "readiness_performance",
                "data": readiness_perf,
                "message": f"Analyzed readiness vs performance across {readiness_perf['data_points']} runs"
            })
        
        # Optimal conditions
        optimal = self.find_optimal_conditions(data)
        if not optimal.get("insufficient_data"):
            insights.append({
                "type": "optimal_conditions",
                "conditions": optimal,
                "message": f"Best runs average: {optimal['avg_pace']:.1f} pace with {optimal['avg_readiness_score']:.0f} readiness"
            })
        
        self.insights = insights
        return insights
    
    def save_insights(self, filename: str = None):
        """Save insights to file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"insights_{timestamp}.json"
        
        filepath = HealthConfig.get_data_path(filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "insights": self.insights
                }, f, indent=2, default=str)
            print(f"Insights saved to {filepath}")
        except Exception as e:
            print(f"Error saving insights: {e}")

if __name__ == "__main__":
    # Test the analytics engine
    analytics = HealthAnalytics()
    
    print("Updating recent data...")
    analytics.collector.update_recent_data(3)
    
    print("Generating insights...")
    insights = analytics.generate_insights()
    
    print(f"Generated {len(insights)} insights:")
    for insight in insights:
        print(f"- {insight['message']}")
    
    analytics.save_insights()
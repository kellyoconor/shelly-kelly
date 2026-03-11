#!/usr/bin/env python3
"""
Quick health check function for Shelly to use in main chats.
"""

import sys
sys.path.append('/data/workspace/health-agent')

def quick_health():
    """Get a quick health summary for chat context."""
    try:
        from data_collector import HealthDataCollector
        
        collector = HealthDataCollector()
        oura_data = collector.collect_oura_data()
        
        if oura_data:
            sleep = oura_data.get("sleep", {})
            readiness = oura_data.get("readiness", {})
            
            sleep_score = sleep.get("score", 0)
            readiness_score = readiness.get("score", 0)
            hrv = readiness.get("hrv_balance", 0)
            
            # Simple prediction
            if readiness_score >= 80 and hrv >= 70:
                training_status = "excellent for training"
            elif readiness_score >= 70 and hrv >= 60:
                training_status = "good for normal training"
            elif readiness_score >= 60:
                training_status = "moderate - take it easier"
            else:
                training_status = "poor - consider rest"
            
            return f"Sleep {sleep_score}, Readiness {readiness_score}, HRV {hrv} → {training_status}"
        else:
            return "No recent health data available"
            
    except Exception as e:
        return f"Health data error: {e}"

if __name__ == "__main__":
    print(quick_health())
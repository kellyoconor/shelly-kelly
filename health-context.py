#!/usr/bin/env python3
"""
Quick health context for main chat sessions.
Simple functions Shelly can call to get Kelly's health insights.
"""

import sys
import os
sys.path.append('/data/workspace/health-agent')

from vault_integration import HealthVaultIntegration, get_health_summary, get_performance_prediction

def get_current_health_status():
    """Get current health status for chat context."""
    try:
        integration = HealthVaultIntegration()
        
        # Get latest brief
        brief = integration.get_latest_brief()
        
        if brief:
            # Extract key metrics from brief
            lines = brief.split('\n')
            oura_line = next((line for line in lines if 'Oura:' in line), '')
            status_line = next((line for line in lines if 'Status:' in line), '')
            prediction_line = next((line for line in lines if 'Performance Prediction:' in line), '')
            
            return {
                "brief": brief,
                "oura_summary": oura_line.replace('💍 **Oura:**', '').strip(),
                "status": status_line.replace('📊 **Status:**', '').strip(),
                "prediction": prediction_line.replace('🎯 **Performance Prediction:**', '').strip()
            }
        else:
            return {"error": "No recent health data available"}
            
    except Exception as e:
        return {"error": f"Health data unavailable: {e}"}

def get_training_recommendation():
    """Get today's training recommendation based on health data."""
    try:
        # Import here to avoid circular imports
        from run_agent import HealthAgent
        
        agent = HealthAgent()
        recommendation = agent.recommend_workout()
        
        return recommendation
        
    except Exception as e:
        return f"Could not generate recommendation: {e}"

def get_recent_patterns(days=7):
    """Get recent health patterns and correlations."""
    try:
        integration = HealthVaultIntegration()
        insights = integration.get_recent_insights(days)
        
        if insights:
            summaries = []
            for insight in insights:
                message = insight.get('message', '')
                if message:
                    summaries.append(message)
            
            return summaries
        else:
            return ["Insufficient data for patterns (need 7+ data points)"]
            
    except Exception as e:
        return [f"Error getting patterns: {e}"]

if __name__ == "__main__":
    # Test the functions
    print("🧪 Testing health context functions...")
    
    status = get_current_health_status()
    print(f"Current status: {status}")
    
    recommendation = get_training_recommendation()
    print(f"Training rec: {recommendation}")
    
    patterns = get_recent_patterns()
    print(f"Patterns: {patterns}")
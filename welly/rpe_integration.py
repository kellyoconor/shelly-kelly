#!/usr/bin/env python3
"""
RPE Integration: Add perceived effort analysis to Welly's insights

Integrates RPE tracking with existing Welly analysis to detect:
- Mind/body misalignment patterns
- Early overreaching signals  
- Recovery effectiveness
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class RPEIntegration:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        
    def analyze_recent_effort_patterns(self, days_back=7):
        """Analyze recent RPE patterns for Welly insights"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Get recent runs with RPE data
        cursor.execute('''
            SELECT 
                date, perceived_effort, effort_vs_hr_delta, 
                leg_feeling, avg_hr, pace, notes
            FROM run_perception 
            WHERE date >= ?
            ORDER BY date DESC
            LIMIT 5
        ''', (cutoff_date,))
        
        runs = cursor.fetchall()
        
        if not runs:
            conn.close()
            return None
            
        insights = self._detect_effort_patterns(runs)
        
        # Also check for chronic patterns
        chronic_insights = self._check_chronic_patterns(cursor, cutoff_date)
        if chronic_insights:
            insights.update(chronic_insights)
        
        conn.close()
        return insights
        
    def _detect_effort_patterns(self, runs):
        """Detect patterns in recent RPE data"""
        insights = {}
        
        # Look for consistent effort/HR mismatches
        high_effort_runs = [r for r in runs if r[2] >= 2]  # effort_vs_hr_delta >= 2
        low_leg_runs = [r for r in runs if r[3] <= 4]      # leg_feeling <= 4
        
        # Pattern 1: Consistently feeling harder than HR suggests
        if len(high_effort_runs) >= 2:
            avg_delta = sum(r[2] for r in high_effort_runs) / len(high_effort_runs)
            insights['mind_body_mismatch'] = {
                'type': 'high_perceived_effort',
                'severity': min(5, int(avg_delta)),
                'message': f"Last {len(high_effort_runs)} runs felt {avg_delta:.1f} points harder than HR data suggests",
                'recommendation': "Consider checking sleep quality, stress levels, or need for recovery",
                'kelly_should_know': len(high_effort_runs) >= 3 or avg_delta >= 3
            }
            
        # Pattern 2: Consistently heavy legs
        if len(low_leg_runs) >= 2:
            avg_legs = sum(r[3] for r in low_leg_runs) / len(low_leg_runs)
            insights['leg_fatigue_pattern'] = {
                'type': 'muscular_fatigue',
                'severity': 5 - int(avg_legs),
                'message': f"Legs consistently feeling heavy (avg {avg_legs:.1f}/10) despite reasonable HR",
                'recommendation': "Focus on recovery activities, stretching, or consider reducing load",
                'kelly_should_know': len(low_leg_runs) >= 3 or avg_legs <= 3
            }
            
        # Pattern 3: Improving trend
        if len(runs) >= 3:
            recent_delta = sum(r[2] for r in runs[:2]) / 2  # Last 2 runs
            older_delta = sum(r[2] for r in runs[-2:]) / 2  # Earlier runs
            
            if recent_delta < older_delta - 1:  # Improving by more than 1 point
                insights['recovery_trend'] = {
                    'type': 'positive_adaptation',
                    'severity': 1,
                    'message': f"Effort vs HR improving - feeling better relative to physiological load",
                    'recommendation': "Good recovery trending - current training load working well",
                    'kelly_should_know': False  # Positive trends don't need alerts
                }
                
        return insights
        
    def _check_chronic_patterns(self, cursor, cutoff_date):
        """Check for longer-term chronic patterns"""
        # Get 2+ weeks of data for chronic pattern detection
        extended_cutoff = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT date, effort_vs_hr_delta, leg_feeling
            FROM run_perception 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (extended_cutoff,))
        
        chronic_runs = cursor.fetchall()
        
        if len(chronic_runs) < 5:
            return None
            
        chronic_insights = {}
        
        # Check for chronic high effort/low HR mismatch (overreaching signal)
        high_effort_count = sum(1 for r in chronic_runs if r[1] >= 2)
        if high_effort_count >= len(chronic_runs) * 0.6:  # 60%+ of runs
            chronic_insights['potential_overreaching'] = {
                'type': 'chronic_mismatch',
                'severity': 4,
                'message': f"Chronic pattern: {high_effort_count}/{len(chronic_runs)} recent runs felt harder than HR suggests",
                'recommendation': "Consider planned recovery block or reducing training intensity",
                'kelly_should_know': True  # This is important to flag
            }
            
        return chronic_insights if chronic_insights else None
        
    def format_kelly_message(self, insights):
        """Format RPE insights for Kelly"""
        if not insights:
            return None
            
        messages = []
        kelly_should_know = False
        
        for insight_type, data in insights.items():
            if data.get('kelly_should_know', False):
                kelly_should_know = True
                messages.append(f"🧠 {data['message']}")
                if data.get('recommendation'):
                    messages.append(f"💡 {data['recommendation']}")
                    
        if kelly_should_know and messages:
            return {
                'kelly_should_know': True,
                'kelly_message': "\n".join(messages),
                'background_info': f"RPE analysis detected {len(insights)} patterns worth attention"
            }
        else:
            return {
                'kelly_should_know': False,
                'background_info': f"RPE tracking: {len(insights)} minor patterns detected, no immediate concerns"
            }

if __name__ == "__main__":
    rpe = RPEIntegration()
    insights = rpe.analyze_recent_effort_patterns()
    
    if insights:
        message = rpe.format_kelly_message(insights)
        print("RPE Analysis Results:")
        print(json.dumps(message, indent=2))
    else:
        print("No recent RPE data to analyze")
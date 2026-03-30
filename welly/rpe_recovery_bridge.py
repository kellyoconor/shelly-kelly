#!/usr/bin/env python3
"""
RPE-Recovery Bridge: Connect RPE tracking with existing recovery systems

Ensures RPE data flows into pattern detection and recovery state assessment
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import existing systems
import importlib.util

# Dynamic imports to handle file naming
def load_module(file_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules
recovery_tracker = load_module('/data/workspace/welly/recovery-tracker.py', 'recovery_tracker')
welly_patterns = load_module('/data/workspace/welly/welly-patterns.py', 'welly_patterns')  
rpe_integration = load_module('/data/workspace/welly/rpe_integration.py', 'rpe_integration')

RecoveryTracker = recovery_tracker.RecoveryTracker
WellyPatterns = welly_patterns.WellyPatterns
RPEIntegration = rpe_integration.RPEIntegration

class RPERecoveryBridge:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        
        # Initialize connected systems
        self.recovery_tracker = RecoveryTracker(workspace)
        self.pattern_detector = WellyPatterns(workspace)
        self.rpe_analyzer = RPEIntegration(workspace)
        
    def analyze_integrated_recovery_state(self, days_back=7):
        """Combine RPE data with existing recovery analysis"""
        
        # Get RPE insights
        rpe_insights = self.rpe_analyzer.analyze_recent_effort_patterns(days_back)
        
        # Get recovery activity patterns
        recovery_gaps = self._check_recovery_activity_gaps(days_back)
        
        # Get objective recovery data (from existing system)
        objective_data = self._get_objective_recovery_data(days_back)
        
        # Combine all data sources
        integrated_state = self._integrate_all_signals(rpe_insights, recovery_gaps, objective_data)
        
        return integrated_state
        
    def _check_recovery_activity_gaps(self, days_back):
        """Check for gaps in recovery activities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Check last recovery activities
        cursor.execute('''
            SELECT activity_type, date, MAX(date) as last_date
            FROM recovery_activities 
            WHERE date >= ?
            GROUP BY activity_type
            ORDER BY last_date DESC
        ''', (cutoff_date,))
        
        activities = cursor.fetchall()
        
        gaps = {}
        today = datetime.now().date()
        
        for activity_type, _, last_date_str in activities:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
            days_since = (today - last_date).days
            
            # Recovery activity thresholds
            thresholds = {
                'stretching': 3,    # Should stretch every 3 days
                'foam_rolling': 4,  # Foam roll every 4 days
                'massage': 14,      # Massage every 2 weeks
                'rest_day': 7       # Rest day weekly
            }
            
            threshold = thresholds.get(activity_type, 7)  # Default 7 days
            
            if days_since > threshold:
                gaps[activity_type] = {
                    'days_since': days_since,
                    'threshold': threshold,
                    'overdue_by': days_since - threshold
                }
        
        conn.close()
        return gaps
        
    def _get_objective_recovery_data(self, days_back):
        """Get objective recovery markers from existing system"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Get recent objective data
        cursor.execute('''
            SELECT date, readiness, hrv_rmssd, resting_hr, sleep_quality, stress
            FROM daily_state 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (cutoff_date,))
        
        objective_data = cursor.fetchall()
        conn.close()
        
        if not objective_data:
            return None
            
        # Analyze trends
        readiness_trend = self._calculate_trend([row[1] for row in objective_data if row[1]])
        hrv_trend = self._calculate_trend([row[2] for row in objective_data if row[2]])
        
        return {
            'readiness_trend': readiness_trend,
            'hrv_trend': hrv_trend,
            'recent_data': objective_data[:3]  # Last 3 days
        }
        
    def _calculate_trend(self, values):
        """Calculate if values are trending up, down, or stable"""
        if len(values) < 2:
            return "insufficient_data"
            
        # Simple trend calculation
        recent_avg = sum(values[:3]) / len(values[:3]) if len(values) >= 3 else values[0]
        older_avg = sum(values[-3:]) / len(values[-3:]) if len(values) >= 3 else values[-1]
        
        diff_pct = ((recent_avg - older_avg) / older_avg) * 100 if older_avg > 0 else 0
        
        if diff_pct > 5:
            return "improving"
        elif diff_pct < -5:
            return "declining"
        else:
            return "stable"
            
    def _integrate_all_signals(self, rpe_insights, recovery_gaps, objective_data):
        """Integrate RPE, recovery activities, and objective data"""
        
        integrated_state = {
            'overall_status': 'unknown',
            'priority_actions': [],
            'patterns_detected': [],
            'kelly_should_know': False,
            'kelly_message': None
        }
        
        concerns = []
        positive_signals = []
        
        # Process RPE insights
        if rpe_insights:
            for insight_type, data in rpe_insights.items():
                if data.get('kelly_should_know', False):
                    concerns.append(f"RPE Pattern: {data['message']}")
                    integrated_state['priority_actions'].append(data.get('recommendation', ''))
                    
        # Process recovery gaps  
        if recovery_gaps:
            overdue_activities = [f"{act} (overdue by {data['overdue_by']} days)" 
                                for act, data in recovery_gaps.items() 
                                if data['overdue_by'] > 2]  # Only flag if >2 days overdue
            if overdue_activities:
                concerns.append(f"Recovery activities overdue: {', '.join(overdue_activities)}")
                integrated_state['priority_actions'].append("Schedule recovery activities")
                
        # Process objective trends
        if objective_data:
            if objective_data['readiness_trend'] == 'declining':
                concerns.append("Readiness trending downward")
            elif objective_data['readiness_trend'] == 'improving':
                positive_signals.append("Readiness improving")
                
            if objective_data['hrv_trend'] == 'declining':
                concerns.append("HRV trending downward")  
            elif objective_data['hrv_trend'] == 'improving':
                positive_signals.append("HRV recovering well")
        
        # Determine overall status
        if len(concerns) >= 2:
            integrated_state['overall_status'] = 'attention_needed'
            integrated_state['kelly_should_know'] = True
            integrated_state['kelly_message'] = f"Recovery check: {'; '.join(concerns[:2])}"
        elif len(concerns) == 1:
            integrated_state['overall_status'] = 'monitor'
        elif positive_signals:
            integrated_state['overall_status'] = 'recovering_well'
        else:
            integrated_state['overall_status'] = 'stable'
            
        integrated_state['patterns_detected'] = concerns + positive_signals
        
        return integrated_state
        
    def check_and_update_recovery_state(self):
        """Main function to check integrated recovery state and update patterns"""
        
        state = self.analyze_integrated_recovery_state()
        
        # Update pattern detection system with new insights
        if state['patterns_detected']:
            for pattern in state['patterns_detected']:
                self._log_pattern_to_memory(pattern)
                
        # Write insight to vault if Kelly should know
        if state['kelly_should_know'] and state['kelly_message']:
            from welly_daily_writer import write_welly_insight
            write_welly_insight(state['kelly_message'], 'recovery')
            
        return state
        
    def _log_pattern_to_memory(self, pattern_description):
        """Log detected pattern to Welly's pattern memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO kelly_patterns (
                pattern_type, pattern_name, description, 
                confidence, last_seen, occurrence_count, created_at
            ) VALUES (?, ?, ?, ?, ?, 
                COALESCE((SELECT occurrence_count FROM kelly_patterns WHERE pattern_name = ?) + 1, 1),
                ?)
        ''', (
            'recovery_integration', 
            f"integrated_recovery_{hash(pattern_description) % 1000}",
            pattern_description,
            0.8,  # High confidence since it's from integrated data
            datetime.now().strftime('%Y-%m-%d'),
            f"integrated_recovery_{hash(pattern_description) % 1000}",
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    bridge = RPERecoveryBridge()
    state = bridge.check_and_update_recovery_state()
    print("Integrated Recovery State:")
    print(json.dumps(state, indent=2))
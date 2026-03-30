#!/usr/bin/env python3
"""
RPE Tracker: Capture perceived effort vs objective data for Welly

Adds post-run perceived effort capture and compares to HR/pace data
to detect recovery patterns and training stress mismatches.
"""

import json
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

class RPETracker:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        
    def setup_rpe_tables(self):
        """Add RPE tracking tables to Welly database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table for post-run perceived effort
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS run_perception (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                run_id TEXT,  -- Strava activity ID
                distance_miles REAL,
                pace TEXT,
                avg_hr INTEGER,
                perceived_effort INTEGER,  -- 1-10 scale
                effort_vs_hr_delta INTEGER,  -- difference from expected
                leg_feeling INTEGER,  -- 1-10 scale (1=dead, 10=bouncy)
                overall_satisfaction INTEGER,  -- 1-10 scale
                notes TEXT,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table for effort/data mismatch patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS effort_mismatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                mismatch_type TEXT,  -- "high_effort_low_hr", "low_effort_high_hr"
                severity INTEGER,    -- 1-5 scale
                context_factors TEXT,  -- sleep, stress, etc.
                pattern_notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def capture_post_run_rpe(self, run_data, perceived_effort, leg_feeling, satisfaction, notes=""):
        """Capture perceived effort after a run"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate effort vs HR delta (simplified - we'd make this more sophisticated)
        expected_effort = self._estimate_expected_effort(run_data['average_heartrate'], run_data['_pace_mi'])
        effort_delta = perceived_effort - expected_effort
        
        cursor.execute('''
            INSERT INTO run_perception (
                date, run_id, distance_miles, pace, avg_hr,
                perceived_effort, effort_vs_hr_delta, leg_feeling,
                overall_satisfaction, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_data['_date'],
            str(run_data['id']),
            run_data['_distance_mi'],
            run_data['_pace_mi'],
            run_data.get('average_heartrate', 0),
            perceived_effort,
            effort_delta,
            leg_feeling,
            satisfaction,
            notes
        ))
        
        # Check for significant mismatch
        if abs(effort_delta) >= 3:  # 3+ point difference
            mismatch_type = "high_effort_low_hr" if effort_delta > 0 else "low_effort_high_hr"
            self._log_effort_mismatch(run_data['_date'], mismatch_type, abs(effort_delta), notes)
        
        conn.commit()
        conn.close()
        
    def _estimate_expected_effort(self, avg_hr, pace):
        """Rough estimate of expected effort based on HR and pace"""
        # This is a simplified model - we'd refine with Kelly's actual data
        if avg_hr < 150:
            return 3  # Easy effort
        elif avg_hr < 160:
            return 5  # Moderate effort  
        elif avg_hr < 170:
            return 7  # Hard effort
        else:
            return 9  # Very hard effort
            
    def _log_effort_mismatch(self, date, mismatch_type, severity, context):
        """Log significant effort/data mismatches for pattern analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO effort_mismatches (
                date, mismatch_type, severity, context_factors, pattern_notes
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            date, mismatch_type, severity, context,
            f"Significant mismatch detected: {mismatch_type} with severity {severity}"
        ))
        
        conn.commit()
        conn.close()
        
    def analyze_effort_patterns(self, days_back=30):
        """Analyze patterns in effort vs data mismatches"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT 
                date, perceived_effort, effort_vs_hr_delta, leg_feeling,
                avg_hr, pace, notes
            FROM run_perception 
            WHERE date >= ?
            ORDER BY date DESC
        ''', (cutoff_date,))
        
        runs = cursor.fetchall()
        
        # Look for patterns
        patterns = {
            'high_effort_low_hr_days': [],
            'consistent_leg_issues': [],
            'recovery_trending': []
        }
        
        for run in runs:
            date, pe, delta, legs, hr, pace, notes = run
            
            # High effort but low HR = potential overreaching/fatigue
            if delta >= 2 and legs <= 5:
                patterns['high_effort_low_hr_days'].append({
                    'date': date, 'delta': delta, 'legs': legs, 'notes': notes
                })
                
            # Consistently poor leg feeling
            if legs <= 4:
                patterns['consistent_leg_issues'].append({
                    'date': date, 'legs': legs, 'hr': hr, 'notes': notes
                })
        
        conn.close()
        return patterns

if __name__ == "__main__":
    tracker = RPETracker()
    tracker.setup_rpe_tables()
    print("✅ RPE tracking tables created/updated")
    
    if len(sys.argv) > 1 and sys.argv[1] == 'analyze':
        patterns = tracker.analyze_effort_patterns()
        print("📊 Effort Pattern Analysis:")
        for pattern_type, events in patterns.items():
            if events:
                print(f"\n{pattern_type}: {len(events)} occurrences")
                for event in events[-3:]:  # Show last 3
                    print(f"  {event}")
#!/usr/bin/env python3
"""
Recovery Activity Tracker for Welly

Simple system to log and track Kelly's recovery activities:
- Stretching sessions
- Foam rolling
- Massage appointments  
- Other recovery work

Integrates with Welly's pattern detection to remind Kelly when gaps occur.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class RecoveryTracker:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.db_path = self.workspace / "welly" / "welly_memory.db"
        self.setup_recovery_tables()
        
    def setup_recovery_tables(self):
        """Create recovery activity tables in Welly database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Recovery activities log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                duration_minutes INTEGER,
                intensity TEXT,
                notes TEXT,
                logged_at TEXT,
                source TEXT DEFAULT 'manual'
            )
        ''')
        
        # Recovery patterns and reminders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recovery_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_name TEXT UNIQUE,
                typical_frequency_days INTEGER,
                last_activity_date TEXT,
                days_since_last INTEGER,
                reminder_threshold_days INTEGER,
                priority_level TEXT DEFAULT 'normal',
                notes TEXT
            )
        ''')
        
        # Initialize default recovery patterns
        cursor.execute('''
            INSERT OR IGNORE INTO recovery_patterns 
            (pattern_name, typical_frequency_days, reminder_threshold_days, priority_level)
            VALUES 
            ('foam_rolling', 3, 5, 'high'),
            ('stretching', 2, 4, 'high'),
            ('massage', 28, 42, 'medium'),
            ('recovery_bath', 7, 10, 'low')
        ''')
        
        conn.commit()
        conn.close()
        
    def log_activity(self, activity_type: str, duration_minutes: int = None, 
                    intensity: str = 'moderate', notes: str = '') -> Dict:
        """Log a recovery activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        logged_at = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO recovery_activities 
            (date, activity_type, duration_minutes, intensity, notes, logged_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (today, activity_type, duration_minutes, intensity, notes, logged_at))
        
        # Update pattern tracking
        cursor.execute('''
            UPDATE recovery_patterns 
            SET last_activity_date = ?, days_since_last = 0
            WHERE pattern_name = ?
        ''', (today, activity_type))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "activity": activity_type,
            "date": today,
            "duration": duration_minutes,
            "message": f"✅ Logged {activity_type} for {duration_minutes or 'unspecified'} minutes"
        }
    
    def check_recovery_gaps(self) -> List[Dict]:
        """Analyze recovery patterns and identify gaps needing attention"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        gaps = []
        
        # Check each recovery pattern for overdue activities
        cursor.execute('''
            SELECT pattern_name, typical_frequency_days, last_activity_date, 
                   reminder_threshold_days, priority_level
            FROM recovery_patterns
        ''')
        
        for row in cursor.fetchall():
            pattern_name, freq_days, last_date, threshold_days, priority = row
            
            if last_date:
                last_activity = datetime.strptime(last_date, '%Y-%m-%d').date()
                days_since = (today - last_activity).days
            else:
                days_since = 999  # Never logged
            
            if days_since >= threshold_days:
                urgency = "overdue" if days_since > threshold_days + 2 else "due"
                
                gaps.append({
                    "activity": pattern_name,
                    "days_since": days_since,
                    "typical_frequency": freq_days,
                    "urgency": urgency,
                    "priority": priority,
                    "message": self._generate_reminder_message(pattern_name, days_since, urgency)
                })
        
        conn.close()
        return sorted(gaps, key=lambda x: (x['priority'] == 'high', x['days_since']), reverse=True)
    
    def _generate_reminder_message(self, activity: str, days_since: int, urgency: str) -> str:
        """Generate Kelly-style reminder messages"""
        
        activity_messages = {
            "foam_rolling": {
                "due": f"Your legs might appreciate some foam rolling - it's been {days_since} days",
                "overdue": f"Those tight spots are probably building up - {days_since} days without foam rolling"
            },
            "stretching": {
                "due": f"Time for some good stretches? Been {days_since} days since your last session",
                "overdue": f"Your body's probably asking for stretches - {days_since} days is longer than usual"
            },
            "massage": {
                "due": f"Massage day coming up? It's been {days_since} days since your last one",
                "overdue": f"Might be time to book that next massage - {days_since} days is getting long"
            },
            "recovery_bath": {
                "due": f"An epsom salt bath might feel good right about now",
                "overdue": f"Some recovery soak time could help - it's been {days_since} days"
            }
        }
        
        return activity_messages.get(activity, {}).get(urgency, 
            f"It's been {days_since} days since your last {activity.replace('_', ' ')}")
    
    def get_recent_activities(self, days: int = 7) -> List[Dict]:
        """Get recovery activities from the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT date, activity_type, duration_minutes, intensity, notes
            FROM recovery_activities
            WHERE date >= ?
            ORDER BY date DESC
        ''', (cutoff_date,))
        
        activities = []
        for row in cursor.fetchall():
            date, activity_type, duration, intensity, notes = row
            activities.append({
                "date": date,
                "activity": activity_type,
                "duration_minutes": duration,
                "intensity": intensity,
                "notes": notes
            })
        
        conn.close()
        return activities
    
    def status(self) -> Dict:
        """Get current recovery status overview"""
        gaps = self.check_recovery_gaps()
        recent = self.get_recent_activities(7)
        
        return {
            "recovery_gaps": gaps,
            "recent_activities": recent,
            "summary": {
                "overdue_activities": len([g for g in gaps if g['urgency'] == 'overdue']),
                "due_activities": len([g for g in gaps if g['urgency'] == 'due']),
                "activities_this_week": len(recent)
            }
        }

def main():
    """Command line interface for recovery tracking"""
    if len(sys.argv) < 2:
        print("""
Recovery Tracker Commands:
  log <activity> [duration] [intensity] [notes]   - Log recovery activity
  status                                           - Check recovery gaps
  recent [days]                                    - Show recent activities
  
Activities: stretching, foam_rolling, massage, recovery_bath

Examples:
  python3 recovery-tracker.py log stretching 15 light "hip flexors"
  python3 recovery-tracker.py log foam_rolling 10
  python3 recovery-tracker.py status
        """)
        return
    
    tracker = RecoveryTracker()
    command = sys.argv[1].lower()
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Usage: log <activity> [duration] [intensity] [notes]")
            return
            
        activity = sys.argv[2]
        duration = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
        intensity = sys.argv[4] if len(sys.argv) > 4 else 'moderate'
        notes = ' '.join(sys.argv[5:]) if len(sys.argv) > 5 else ''
        
        result = tracker.log_activity(activity, duration, intensity, notes)
        print(result['message'])
        
    elif command == "status":
        status = tracker.status()
        
        print("🔄 Recovery Status")
        print("=" * 30)
        
        if status['recovery_gaps']:
            print("\n⚠️ Recovery Gaps:")
            for gap in status['recovery_gaps']:
                print(f"  • {gap['message']}")
        else:
            print("\n✅ All recovery activities up to date!")
        
        if status['recent_activities']:
            print(f"\n📋 Recent Activities ({len(status['recent_activities'])} this week):")
            for activity in status['recent_activities'][:5]:
                duration_str = f" ({activity['duration_minutes']}min)" if activity['duration_minutes'] else ""
                print(f"  • {activity['date']}: {activity['activity']}{duration_str}")
        
    elif command == "recent":
        days = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 7
        activities = tracker.get_recent_activities(days)
        
        print(f"📋 Recovery Activities (last {days} days)")
        print("=" * 40)
        
        if activities:
            for activity in activities:
                duration_str = f" ({activity['duration_minutes']}min)" if activity['duration_minutes'] else ""
                notes_str = f" - {activity['notes']}" if activity['notes'] else ""
                print(f"  {activity['date']}: {activity['activity']}{duration_str}{notes_str}")
        else:
            print("  No recovery activities logged recently")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    import sys
    main()
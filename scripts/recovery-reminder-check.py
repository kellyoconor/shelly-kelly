#!/usr/bin/env python3
"""
Recovery Reminder Check for Heartbeat System

Checks for recovery activity gaps and returns reminder messages
for integration with Shelly's heartbeat system.
"""

import sys
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def setup_recovery_db():
    """Ensure recovery tables exist"""
    db_path = Path("/data/workspace/welly/welly_memory.db")
    if not db_path.exists():
        return False
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tables exist
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='recovery_activities'
    ''')
    
    if not cursor.fetchone():
        # Initialize recovery system
        cursor.execute('''
            CREATE TABLE recovery_activities (
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
        
        cursor.execute('''
            CREATE TABLE recovery_patterns (
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
        
        # Initialize patterns
        cursor.execute('''
            INSERT INTO recovery_patterns 
            (pattern_name, typical_frequency_days, reminder_threshold_days, priority_level)
            VALUES 
            ('foam_rolling', 3, 4, 'high'),
            ('stretching', 2, 3, 'high'),
            ('massage', 28, 42, 'medium'),
            ('recovery_bath', 7, 10, 'low')
        ''')
        
        conn.commit()
    
    conn.close()
    return True

def check_recovery_reminders():
    """Check for recovery activities that need attention"""
    if not setup_recovery_db():
        return None
    
    db_path = Path("/data/workspace/welly/welly_memory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = datetime.now().date()
    reminders = []
    
    # Check patterns for overdue activities
    cursor.execute('''
        SELECT pattern_name, typical_frequency_days, last_activity_date, 
               reminder_threshold_days, priority_level
        FROM recovery_patterns
        ORDER BY priority_level = 'high' DESC, reminder_threshold_days ASC
    ''')
    
    for row in cursor.fetchall():
        pattern_name, freq_days, last_date, threshold_days, priority = row
        
        if last_date:
            last_activity = datetime.strptime(last_date, '%Y-%m-%d').date()
            days_since = (today - last_activity).days
        else:
            days_since = 999  # Never logged
        
        if days_since >= threshold_days:
            urgency = "overdue" if days_since > threshold_days + 1 else "due"
            
            # Generate contextual reminders based on activity and timing
            if pattern_name == "foam_rolling" and days_since < 100:
                if urgency == "overdue":
                    message = f"Your legs might be asking for some foam rolling - it's been {days_since} days 🫠"
                else:
                    message = f"Foam rolling check: {days_since} days since your last session"
                    
            elif pattern_name == "stretching" and days_since < 100:
                if urgency == "overdue":
                    message = f"Time for some good stretches? Been {days_since} days - your body's probably ready ⏰"
                else:
                    message = f"Stretch check: {days_since} days - feeling tight anywhere?"
                    
            elif pattern_name == "recovery_bath" and days_since < 100:
                message = f"An epsom salt bath might feel good - it's been {days_since} days since you had some soak time 🛁"
                
            elif pattern_name == "massage" and days_since < 100:
                message = f"Massage window coming up - been {days_since} days since your last appointment"
            
            else:
                continue  # Skip if never tracked or not actionable
            
            reminders.append({
                "activity": pattern_name,
                "days_since": days_since,
                "urgency": urgency,
                "priority": priority,
                "message": message
            })
    
    conn.close()
    
    # Return the highest priority reminder
    if reminders:
        # Sort by priority and urgency
        reminders.sort(key=lambda x: (
            x['priority'] == 'high',  # High priority first
            x['urgency'] == 'overdue',  # Overdue before due
            -x['days_since']  # Most overdue first
        ), reverse=True)
        
        return reminders[0]
    
    return None

def main():
    """Check for recovery reminders and output the most urgent one"""
    reminder = check_recovery_reminders()
    
    if reminder:
        print(reminder['message'])
    else:
        # Return nothing if no reminders needed
        pass

if __name__ == "__main__":
    main()
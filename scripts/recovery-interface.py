#!/usr/bin/env python3
"""
Simple Recovery Interface for Kelly

Handles WhatsApp messages for recovery activity logging and status checks.
Integrates with Welly's recovery tracking system.
"""

import sys
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def setup_recovery_db():
    """Setup recovery tables in Welly database"""
    db_path = Path("/data/workspace/welly/welly_memory.db")
    conn = sqlite3.connect(db_path)
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
            source TEXT DEFAULT 'whatsapp'
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

def log_recovery_activity(activity_type: str, duration_minutes: int = None, 
                         intensity: str = 'moderate', notes: str = ''):
    """Log a recovery activity"""
    setup_recovery_db()
    
    db_path = Path("/data/workspace/welly/welly_memory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    logged_at = datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO recovery_activities 
        (date, activity_type, duration_minutes, intensity, notes, logged_at, source)
        VALUES (?, ?, ?, ?, ?, ?, 'whatsapp')
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
        "duration": duration_minutes
    }

def check_recovery_status():
    """Check recovery gaps and generate status report"""
    setup_recovery_db()
    
    db_path = Path("/data/workspace/welly/welly_memory.db")
    conn = sqlite3.connect(db_path)
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
            message = generate_reminder_message(pattern_name, days_since, urgency)
            
            gaps.append({
                "activity": pattern_name,
                "days_since": days_since,
                "urgency": urgency,
                "priority": priority,
                "message": message
            })
    
    conn.close()
    return gaps

def generate_reminder_message(activity: str, days_since: int, urgency: str) -> str:
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
            "due": f"Next massage coming up? It's been {days_since} days since your last one",
            "overdue": f"Your next massage window is here - {days_since} days since the last one"
        },
        "recovery_bath": {
            "due": f"An epsom salt bath might feel good right about now",
            "overdue": f"Some recovery soak time could help - it's been {days_since} days"
        }
    }
    
    if days_since > 100:  # Never done
        return f"Haven't tracked any {activity.replace('_', ' ')} yet - want to start logging it?"
    
    return activity_messages.get(activity, {}).get(urgency, 
        f"It's been {days_since} days since your last {activity.replace('_', ' ')}")

def get_recent_activities(days: int = 7):
    """Get recent recovery activities"""
    setup_recovery_db()
    
    db_path = Path("/data/workspace/welly/welly_memory.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT date, activity_type, duration_minutes, notes
        FROM recovery_activities
        WHERE date >= ?
        ORDER BY date DESC
    ''', (cutoff_date,))
    
    activities = []
    for row in cursor.fetchall():
        date, activity_type, duration, notes = row
        activities.append({
            "date": date,
            "activity": activity_type,
            "duration_minutes": duration,
            "notes": notes
        })
    
    conn.close()
    return activities

def sync_to_vault(activity_result):
    """Sync recovery activity to Kelly's daily note in vault"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        vault_daily_note = Path(f"/data/kelly-vault/01-Daily/2026/{today}.md")
        
        if not vault_daily_note.exists():
            return  # Don't create notes, just add to existing ones
        
        # Read current note
        content = vault_daily_note.read_text()
        
        # Prepare the Welly entry
        activity_name = activity_result['activity'].replace('_', ' ').title()
        duration_str = f" ({activity_result['duration']}min)" if activity_result['duration'] else ""
        timestamp = datetime.now().strftime('%H:%M')
        welly_entry = f"- **{timestamp}**: {activity_name}{duration_str}"
        
        # Find or create Welly section
        if "## Welly" in content:
            # Add to existing Welly section
            welly_section_start = content.find("## Welly")
            next_section = content.find("\n## ", welly_section_start + 1)
            
            if next_section == -1:  # Welly section is last
                # Add to end of Welly section
                content = content.rstrip() + "\n" + welly_entry + "\n"
            else:
                # Insert before next section
                before_next = content[:next_section]
                after_next = content[next_section:]
                content = before_next.rstrip() + "\n" + welly_entry + "\n\n" + after_next
        else:
            # Create new Welly section at end
            content = content.rstrip() + "\n\n## Welly\n" + welly_entry + "\n"
        
        # Write back to file
        vault_daily_note.write_text(content)
        
    except Exception as e:
        # Fail silently - vault sync is nice-to-have, not critical
        pass

def parse_recovery_message(message: str):
    """Parse WhatsApp messages for recovery activity logging"""
    message = message.lower().strip()
    
    # Status check patterns
    if any(phrase in message for phrase in ['recovery status', 'recovery check', 'recovery gaps', 'how am i doing recovery']):
        return {'command': 'status'}
    
    # Recent activities patterns  
    if any(phrase in message for phrase in ['recent recovery', 'what recovery', 'recovery recent']):
        return {'command': 'recent'}
    
    # Activity logging patterns
    log_patterns = [
        r"logged (\w+)(?:\s+(\d+))?",
        r"did (\w+)(?:\s+for\s+(\d+))?",
        r"had (\w+)(?:\s+(\d+))?",
        r"(\w+) done(?:\s+(\d+))?",
        r"just did (\w+)(?:\s+(\d+))?"
    ]
    
    for pattern in log_patterns:
        match = re.search(pattern, message)
        if match:
            activity = match.group(1)
            duration = int(match.group(2)) if match.group(2) else None
            
            # Map common aliases
            activity_aliases = {
                'stretching': 'stretching',
                'stretch': 'stretching', 
                'stretches': 'stretching',
                'foam': 'foam_rolling',
                'rolling': 'foam_rolling',
                'massage': 'massage',
                'bath': 'recovery_bath',
                'soak': 'recovery_bath'
            }
            
            activity = activity_aliases.get(activity, activity)
            
            return {
                'command': 'log',
                'activity': activity,
                'duration': duration
            }
    
    return None

def process_recovery_message(message: str) -> str:
    """Process recovery-related message and return response"""
    parsed = parse_recovery_message(message)
    
    if not parsed:
        return ""  # Not a recovery-related message
    
    if parsed['command'] == 'status':
        gaps = check_recovery_status()
        recent = get_recent_activities(7)
        
        if not gaps:
            if recent:
                return f"✅ Recovery looking good! You've done {len(recent)} activities this week."
            else:
                return "✅ No recovery gaps detected (though you haven't logged anything recently)."
        
        response = "🔄 Recovery check:\n"
        
        # Show most urgent gaps
        urgent_gaps = [g for g in gaps if g['urgency'] == 'overdue' and g['days_since'] < 100][:2]
        due_gaps = [g for g in gaps if g['urgency'] == 'due' and g['days_since'] < 100][:2]
        
        if urgent_gaps:
            response += "\n⚠️ Overdue:\n"
            for gap in urgent_gaps:
                response += f"• {gap['message']}\n"
        
        if due_gaps:
            response += "\n📋 Coming up:\n"
            for gap in due_gaps:
                response += f"• {gap['message']}\n"
        
        return response.strip()
    
    elif parsed['command'] == 'recent':
        activities = get_recent_activities(7)
        
        if not activities:
            return "📋 No recovery activities logged this week yet."
        
        response = f"📋 Recovery this week ({len(activities)} activities):\n"
        for activity in activities[:5]:
            duration_str = f" ({activity['duration_minutes']}min)" if activity['duration_minutes'] else ""
            response += f"• {activity['date']}: {activity['activity'].replace('_', ' ')}{duration_str}\n"
        
        return response.strip()
    
    elif parsed['command'] == 'log':
        result = log_recovery_activity(parsed['activity'], parsed['duration'])
        
        if result['success']:
            # Also log to vault daily note
            sync_to_vault(result)
            
            duration_str = f" for {result['duration']} minutes" if result['duration'] else ""
            return f"✅ Logged {result['activity'].replace('_', ' ')}{duration_str}! Nice work 🙌"
        else:
            return "Oops, couldn't log that recovery activity."
    
    return ""

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: python3 recovery-interface.py \"message\"")
        print("\nExamples:")
        print("  'logged stretching 15'")
        print("  'did foam rolling'") 
        print("  'recovery status'")
        return
    
    message = ' '.join(sys.argv[1:])
    response = process_recovery_message(message)
    
    if response:
        print(response)
    else:
        print("Not a recovery-related message")

if __name__ == "__main__":
    main()
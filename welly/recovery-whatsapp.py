#!/usr/bin/env python3
"""
WhatsApp Interface for Recovery Tracker

Simple commands Kelly can use via WhatsApp to log recovery activities:
- "logged stretching 15"
- "did foam rolling"  
- "recovery status"
"""

import sys
import re
import os

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recovery_tracker import RecoveryTracker

def parse_recovery_message(message: str):
    """Parse WhatsApp messages for recovery activity logging"""
    message = message.lower().strip()
    
    # Patterns for logging activities
    log_patterns = [
        r"logged (\w+)(?:\s+(\d+))?(?:\s+(light|moderate|intense))?",
        r"did (\w+)(?:\s+for\s+(\d+))?(?:\s+minutes?)?",
        r"had (\w+)(?:\s+(\d+))?(?:\s+min)?",
        r"(\w+) done(?:\s+(\d+))?(?:\s+minutes?)?",
    ]
    
    # Check for status request
    if any(word in message for word in ['recovery status', 'recovery check', 'recovery gaps']):
        return {'command': 'status'}
    
    # Check for recent activities request
    if 'recent recovery' in message or 'what have i done' in message:
        return {'command': 'recent'}
    
    # Try to parse activity logging
    for pattern in log_patterns:
        match = re.search(pattern, message)
        if match:
            activity = match.group(1)
            duration = int(match.group(2)) if match.group(2) else None
            intensity = match.group(3) if len(match.groups()) > 2 and match.group(3) else 'moderate'
            
            # Map common aliases
            activity_aliases = {
                'stretching': 'stretching',
                'stretch': 'stretching',
                'stretches': 'stretching',
                'foam': 'foam_rolling',
                'foam_rolling': 'foam_rolling',
                'rolling': 'foam_rolling',
                'massage': 'massage',
                'bath': 'recovery_bath',
                'soak': 'recovery_bath',
                'epsom': 'recovery_bath'
            }
            
            activity = activity_aliases.get(activity, activity)
            
            return {
                'command': 'log',
                'activity': activity,
                'duration': duration,
                'intensity': intensity
            }
    
    return None

def process_recovery_message(message: str) -> str:
    """Process recovery-related WhatsApp message and return response"""
    parsed = parse_recovery_message(message)
    
    if not parsed:
        return "I didn't recognize that as a recovery command. Try: 'logged stretching 15' or 'recovery status'"
    
    tracker = RecoveryTracker()
    
    if parsed['command'] == 'status':
        status = tracker.status()
        
        if not status['recovery_gaps']:
            return "✅ All your recovery work is up to date! Looking good."
        
        response = "🔄 Recovery check:\n"
        
        # Show most urgent gaps
        urgent_gaps = [g for g in status['recovery_gaps'] if g['urgency'] == 'overdue'][:2]
        due_gaps = [g for g in status['recovery_gaps'] if g['urgency'] == 'due'][:2]
        
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
        activities = tracker.get_recent_activities(7)
        
        if not activities:
            return "No recovery activities logged this week. Time to get started! 💪"
        
        response = f"📋 Recovery this week ({len(activities)} activities):\n"
        for activity in activities[:5]:
            duration_str = f" ({activity['duration_minutes']}min)" if activity['duration_minutes'] else ""
            response += f"• {activity['date']}: {activity['activity'].replace('_', ' ')}{duration_str}\n"
        
        return response.strip()
    
    elif parsed['command'] == 'log':
        result = tracker.log_activity(
            parsed['activity'], 
            parsed['duration'], 
            parsed['intensity']
        )
        
        if result['success']:
            return f"{result['message']} 🙌"
        else:
            return f"Oops, couldn't log that: {result.get('error', 'Unknown error')}"
    
    return "Something went wrong processing your recovery message."

def main():
    """Test interface from command line"""
    if len(sys.argv) < 2:
        print("Usage: python3 recovery-whatsapp.py \"message text\"")
        print("\nTest messages:")
        print("  'logged stretching 15'")
        print("  'did foam rolling'")
        print("  'recovery status'")
        return
    
    message = ' '.join(sys.argv[1:])
    response = process_recovery_message(message)
    print(response)

if __name__ == "__main__":
    main()
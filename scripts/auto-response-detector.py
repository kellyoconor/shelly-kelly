#!/usr/bin/env python3
"""
Auto Response Detector
Call this script with Kelly's message to automatically detect what she's responding to
and mark those topics as discussed to prevent repetition.

Usage: python3 auto-response-detector.py "Kelly's message text here"
"""

import sys
import os

# Import the function directly
sys.path.insert(0, '/data/workspace/scripts')

# Import with full path approach
def detect_and_record_response(user_message):
    """Copy of function to avoid import issues"""
    import json
    from datetime import datetime
    
    try:
        session_state_file = "/data/workspace/memory/session-discussion-state.json"
        message_lower = user_message.lower()
        
        # Load current state
        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            session_state = {}
        
        # Ensure structure exists
        if 'discussed_topics' not in session_state:
            session_state['discussed_topics'] = {}
        
        # Detect responses to different question types
        detected_topics = []
        
        # Running responses
        if any(phrase in message_lower for phrase in [
            'rest day', 'no run', 'didn\'t run', 'haven\'t run', 'not running',
            'ran ', 'going to run', 'will run', 'planning to run'
        ]):
            detected_topics.append('running')
        
        # Health/energy responses  
        if any(phrase in message_lower for phrase in [
            'feeling', 'energy', 'tired', 'good', 'ok', 'fine', 'great', 
            'exhausted', 'ready', 'sleep', 'rested'
        ]):
            detected_topics.append('health_data')
            
        # Coffee/morning routine responses
        if any(phrase in message_lower for phrase in [
            'coffee', 'starbucks', 'caffeine', 'morning', 'usual order',
            'hazelnut', 'vanilla', 'iced coffee'
        ]):
            detected_topics.append('morning_routine')
            
        # Work/project responses
        if any(phrase in message_lower for phrase in [
            'steely', 'development', 'coding', 'working on', 'project',
            'breakthrough', 'progress'
        ]):
            detected_topics.append('current_work')
            
        # Calendar/system responses  
        if any(phrase in message_lower for phrase in [
            'calendar', 'auth', 'authentication', 'fix', 'broken'
        ]):
            detected_topics.append('calendar')
        
        # Record all detected topics
        for topic in detected_topics:
            session_state['discussed_topics'][topic] = True
            
        session_state['last_updated'] = datetime.now().isoformat()
        
        # Save back
        with open(session_state_file, 'w') as f:
            json.dump(session_state, f, indent=2)
            
        return detected_topics
        
    except Exception as e:
        return []

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto-response-detector.py \"message text\"")
        return
    
    user_message = sys.argv[1]
    detected_topics = detect_and_record_response(user_message)
    
    if detected_topics:
        print(f"✅ Auto-detected response to: {', '.join(detected_topics)}")
        print("These topics marked as discussed to prevent repetition.")
    else:
        print("No specific topic responses detected.")

if __name__ == "__main__":
    main()
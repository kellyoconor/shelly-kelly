#!/usr/bin/env python3
"""
Context Significance Checker
Analyzes recent memory to identify significant events that warrant personal check-ins
Tracks what it's asked about recently to avoid repetition
FIXED: Now includes logic to stay quiet when appropriate
"""

import os
import json
from datetime import datetime, timedelta

TRACKING_FILE = "/data/workspace/memory/context-check-history.json"

def load_tracking_history():
    """Load history of what we've asked about recently"""
    if not os.path.exists(TRACKING_FILE):
        return {}
    
    try:
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_tracking_history(history):
    """Save history of what we've asked about"""
    try:
        with open(TRACKING_FILE, 'w') as f:
            json.dump(history, f, indent=2)
    except:
        pass

def was_recently_asked(topic_type, hours=6):
    """Check if we've asked about this topic recently"""
    history = load_tracking_history()
    
    if topic_type not in history:
        return False
    
    last_asked = datetime.fromisoformat(history[topic_type])
    cutoff = datetime.now() - timedelta(hours=hours)
    
    return last_asked > cutoff

def should_stay_quiet():
    """Determine if we should stay quiet instead of sending a check-in"""
    current_time = datetime.now()
    hour = current_time.hour
    
    # Quiet hours: Late night (23:00-06:00)
    if hour >= 23 or hour <= 6:
        return True
    
    # Check if we've sent ANY message recently (not just topic-specific)
    history = load_tracking_history()
    
    if 'last_general_checkin' in history:
        last_checkin = datetime.fromisoformat(history['last_general_checkin'])
        # Minimum 2 hours between ANY proactive check-ins
        if datetime.now() - last_checkin < timedelta(hours=2):
            return True
    
    # Stay quiet if we've asked about multiple topics recently (avoid chattiness)
    recent_topics = 0
    cutoff = datetime.now() - timedelta(hours=6)
    
    for topic, timestamp_str in history.items():
        if topic == 'last_general_checkin':
            continue
        try:
            if datetime.fromisoformat(timestamp_str) > cutoff:
                recent_topics += 1
        except:
            continue
    
    # If we've covered 2+ topics in last 6 hours, stay quiet
    if recent_topics >= 2:
        return True
        
    return False

def mark_as_asked(topic_type):
    """Mark that we've asked about this topic"""
    history = load_tracking_history()
    now = datetime.now().isoformat()
    history[topic_type] = now
    
    # Also track that we sent a general check-in
    history['last_general_checkin'] = now
    
    save_tracking_history(history)

def analyze_recent_context():
    """Check for significant events in recent memory files"""
    significance_flags = []
    
    # Only check TODAY'S memory for current events (yesterday's events are not current)
    today = datetime.now().strftime("%Y-%m-%d")
    
    content = ""
    memory_file = f"/data/workspace/memory/{today}.md"
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as f:
            raw_content = f.read()
            
        # Filter out issue descriptions and past problems to avoid false positives
        lines = raw_content.split('\n')
        filtered_lines = []
        for line in lines:
            # Skip lines that are clearly about past issues, not current events
            if any(marker in line.lower() for marker in ['**issue**:', '- **issue**:', 'timeframe confusion', 'bug report', 'past problem']):
                continue
            filtered_lines.append(line)
        
        content = ' '.join(filtered_lines).lower()
            
    # Flag significant events (but check if we've asked recently)
    
    # Career/Work milestones
    if (any(word in content for word in ['promotion', 'promoted', 'director', 'career milestone', 'new title', 'comp bump']) 
        and not was_recently_asked('career_milestone', hours=4)):
        significance_flags.append({
            "type": "career_milestone", 
            "message": "Kelly! 🎉 That promotion is such a huge milestone. How are you feeling about it now that it's had some time to sink in?"
        })
        
    # Personal/emotional processing  
    elif (any(phrase in content for phrase in ['feeling alone', 'alone with', 'no one to share', 'celebrate alone', 'by myself'])
          and not was_recently_asked('emotional_processing', hours=4)):
        significance_flags.append({
            "type": "emotional_processing",
            "message": "Sensed you might be processing some complex feelings today. Want to talk about what's on your mind?"
        })
    
    # Technical work
    elif (any(word in content for word in ['massive', 'epic', 'marathon', 'built', 'cognitive architecture'])
          and not was_recently_asked('big_building_day', hours=6)):
        significance_flags.append({
            "type": "big_building_day",
            "message": "You had a massive engineering day building cognitive architecture. How are you feeling after all that intensive work?"
        })
        
    # Problem solving
    elif (any(word in content for word in ['bug', 'debugging', 'fixed', 'problem'])
          and not was_recently_asked('problem_solving', hours=6)):
        significance_flags.append({
            "type": "problem_solving",
            "message": "Saw you were debugging some complex issues today. Feeling satisfied with the fixes or still thinking about it?"
        })
        
    # Organization work
    elif (any(word in content for word in ['consolidation', 'cleanup', 'organized'])
          and not was_recently_asked('organization', hours=8)):
        significance_flags.append({
            "type": "organization",
            "message": "Noticed you did some organizing and cleanup work. Feel more grounded with things tidied up?"
        })
    
    # Check MEMORY.md for ongoing situations (lower priority)
    memory_file = "/data/workspace/MEMORY.md"
    if os.path.exists(memory_file) and not significance_flags:
        with open(memory_file, 'r') as f:
            memory_content = f.read()
            
        # Look for unresolved items or current projects
        if "nantucket" in memory_content.lower() and not was_recently_asked('upcoming_trip', hours=24):
            significance_flags.append({
                "type": "upcoming_trip", 
                "message": "How's the Nantucket trip planning coming along? Excited about June?"
            })
    
    return significance_flags

def get_personal_checkin():
    """Get a personal check-in question based on recent context"""
    # NEW: Check if we should stay quiet first
    if should_stay_quiet():
        return ""  # Return empty string to stay quiet
    
    significance_flags = analyze_recent_context()
    
    if significance_flags:
        # Mark that we're asking about this topic
        topic = significance_flags[0]
        mark_as_asked(topic["type"])
        return topic["message"]
    else:
        # NEW: Only send default check-ins occasionally, not every heartbeat
        # Check if it's been at least 4 hours since any check-in
        history = load_tracking_history()
        if 'last_general_checkin' in history:
            last_checkin = datetime.fromisoformat(history['last_general_checkin'])
            # Require 4+ hours between generic check-ins
            if datetime.now() - last_checkin < timedelta(hours=4):
                return ""  # Stay quiet
        
        # Send a default caring check-in (but mark it so we don't spam)
        defaults = [
            "How's your energy today? Feeling aligned or scattered?",
            "What's on your mind lately? Anything you're processing?", 
            "How are you feeling about the week ahead?",
            "Everything running smooth - how are YOU doing?"
        ]
        
        # Simple rotation based on hour
        hour = datetime.now().hour
        message = defaults[hour % len(defaults)]
        
        # Mark that we sent a general check-in
        mark_as_asked('general_checkin')
        
        return message

if __name__ == "__main__":
    result = get_personal_checkin()
    if result:
        print(result)
    # If empty, print nothing (script will return nothing to heartbeat)
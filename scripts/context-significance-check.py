#!/usr/bin/env python3
"""
Context Significance Checker
Analyzes recent memory to identify significant events that warrant personal check-ins
Tracks what it's asked about recently to avoid repetition
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

def mark_as_asked(topic_type):
    """Mark that we've asked about this topic"""
    history = load_tracking_history()
    history[topic_type] = datetime.now().isoformat()
    save_tracking_history(history)

def analyze_recent_context():
    """Check for significant events in recent memory files"""
    significance_flags = []
    
    # Check today's and yesterday's memory files (significant events can span days)
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    content = ""
    for date_str in [today, yesterday]:
        memory_file = f"/data/workspace/memory/{date_str}.md"
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                content += f.read().lower() + " "
            
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
    significance_flags = analyze_recent_context()
    
    if significance_flags:
        # Mark that we're asking about this topic
        topic = significance_flags[0]
        mark_as_asked(topic["type"])
        return topic["message"]
    else:
        # Default caring check-ins (rotate these)
        defaults = [
            "How's your energy today? Feeling aligned or scattered?",
            "What's on your mind lately? Anything you're processing?", 
            "How are you feeling about the week ahead?",
            "Everything running smooth - how are YOU doing?"
        ]
        
        # Simple rotation based on hour
        hour = datetime.now().hour
        return defaults[hour % len(defaults)]

if __name__ == "__main__":
    result = get_personal_checkin()
    print(result)
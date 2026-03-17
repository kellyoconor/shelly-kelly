#!/usr/bin/env python3
"""
Context Significance Checker
Analyzes recent memory to identify significant events that warrant personal check-ins
"""

import os
from datetime import datetime, timedelta

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
            
        # Flag significant events
        
        # Career/Work milestones
        if any(word in content for word in ['promotion', 'promoted', 'director', 'career milestone', 'new title', 'comp bump']):
            significance_flags.append({
                "type": "career_milestone", 
                "message": "Director Kelly O'Conor! 🎉 That's a huge milestone. How are you feeling about it now that it's had some time to sink in?"
            })
            
        # Personal/emotional processing
        if any(phrase in content for phrase in ['feeling alone', 'alone with', 'no one to share', 'celebrate alone', 'by myself']):
            significance_flags.append({
                "type": "emotional_processing",
                "message": "Sensed you might be processing some complex feelings today. Want to talk about what's on your mind?"
            })
        
        if any(word in content for word in ['massive', 'epic', 'marathon', 'built', 'cognitive architecture']):
            significance_flags.append({
                "type": "big_building_day",
                "message": "You had a massive engineering day building cognitive architecture. How are you feeling after all that intensive work?"
            })
            
        if any(word in content for word in ['bug', 'debugging', 'fixed', 'problem']):
            significance_flags.append({
                "type": "problem_solving",
                "message": "Saw you were debugging some complex issues today. Feeling satisfied with the fixes or still thinking about it?"
            })
            
        if any(word in content for word in ['consolidation', 'cleanup', 'organized']):
            significance_flags.append({
                "type": "organization",
                "message": "Noticed you did some organizing and cleanup work. Feel more grounded with things tidied up?"
            })
    
    # Check MEMORY.md for ongoing situations
    memory_file = "/data/workspace/MEMORY.md"
    if os.path.exists(memory_file):
        with open(memory_file, 'r') as f:
            memory_content = f.read()
            
        # Look for unresolved items or current projects
        if "nantucket" in memory_content.lower():
            significance_flags.append({
                "type": "upcoming_trip", 
                "message": "How's the Nantucket trip planning coming along? Excited about June?"
            })
    
    return significance_flags

def get_personal_checkin():
    """Get a personal check-in question based on recent context"""
    significance_flags = analyze_recent_context()
    
    if significance_flags:
        # Return most relevant check-in
        return significance_flags[0]["message"]
    else:
        # Default caring check-ins
        defaults = [
            "How's your energy today? Feeling aligned or scattered?",
            "What's on your mind lately? Anything you're processing?", 
            "How are you feeling about the week ahead?"
        ]
        return defaults[0]  # Could rotate these

if __name__ == "__main__":
    result = get_personal_checkin()
    print(result)
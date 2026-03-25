#!/usr/bin/env python3
"""
Combined Context Checker
Runs both full context check (Strava, Oura, calendar) AND significance check (memory analysis)
Merges results intelligently to prioritize the most relevant check-in
"""

import subprocess
import sys
import json
from datetime import datetime

def run_full_context_check():
    """Get external data context (Strava, Oura, calendar)"""
    try:
        result = subprocess.run(['python3', '/data/workspace/scripts/full-context-check.py'], 
                               capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            output = result.stdout
            
            # Parse key external events
            external_events = {}
            
            # Check for runs today
            if "✅ Ran today:" in output:
                run_line = [l for l in output.split('\n') if "✅ Ran today:" in l][0]
                external_events['run_today'] = run_line.replace('🏃‍♀️ Running: ', '')
                
            # Check for calendar issues
            if "🔒 Calendar auth expired" in output:
                external_events['calendar_auth'] = "Calendar authentication expired"
                
            # Check for health data
            health_lines = [l for l in output.split('\n') if l.startswith('💍 Health:')]
            if health_lines:
                external_events['health'] = health_lines[0].replace('💍 Health: ', '')
            
            return external_events
        else:
            return {"error": "Full context check failed"}
            
    except Exception as e:
        return {"error": f"Full context error: {str(e)[:50]}"}

def run_significance_check():
    """Get memory-based significance analysis"""
    try:
        result = subprocess.run(['python3', '/data/workspace/scripts/context-significance-check.py'], 
                               capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0 and result.stdout.strip():
            return {"significance_message": result.stdout.strip()}
        else:
            return {"no_significance": True}
            
    except Exception as e:
        return {"error": f"Significance check error: {str(e)[:50]}"}

def merge_contexts(external_events, significance_result):
    """Merge external and significance contexts intelligently"""
    messages = []
    
    # Priority 1: Recent runs (Kelly specifically called this out)
    if 'run_today' in external_events:
        run_info = external_events['run_today']
        messages.append(f"Nice work on your run! {run_info} - how did it feel? 🏃‍♀️")
        
    # Priority 2: Significant emotional/personal processing 
    elif 'significance_message' in significance_result:
        messages.append(significance_result['significance_message'])
        
    # Priority 3: Health insights + external context
    elif 'health' in external_events and any(emoji in external_events['health'] for emoji in ['😴', '🥱', '💪']):
        health_msg = external_events['health']
        if '😴' in health_msg or '🥱' in health_msg:
            messages.append(f"Your body's telling a story today: {health_msg}. How are you feeling energy-wise?")
        else:
            messages.append(f"Looking strong: {health_msg}. How's your energy matching the data?")
            
    # Priority 4: System issues (calendar auth, etc.)
    elif 'calendar_auth' in external_events:
        messages.append("Quick heads up - your calendar authentication expired and might need a refresh 📅")
        
    # Default: General caring check-in
    else:
        messages.append("Everything running smooth - how are YOU doing?")
    
    return messages[0] if messages else ""

def get_combined_context():
    """Run both checks and return the most appropriate message"""
    
    # Run both checks
    external_events = run_full_context_check()
    significance_result = run_significance_check()
    
    # Handle errors gracefully
    if "error" in external_events and "error" in significance_result:
        return "How's your day going? (Context checks temporarily unavailable)"
    
    # If one failed, use the other
    if "error" in external_events:
        if 'significance_message' in significance_result:
            return significance_result['significance_message']
        else:
            return "How are you feeling today?"
            
    if "error" in significance_result:
        if 'run_today' in external_events:
            run_info = external_events['run_today']
            return f"Saw your run! {run_info} - how did it feel? 🏃‍♀️"
        else:
            return "Everything running smooth - how are YOU doing?"
    
    # Both successful - merge intelligently
    return merge_contexts(external_events, significance_result)

if __name__ == "__main__":
    result = get_combined_context()
    if result:
        print(result)
    # If empty, print nothing (heartbeat will continue to other checks)
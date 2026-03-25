#!/usr/bin/env python3
"""
Combined Context Checker
Runs both full context check (Strava, Oura, calendar) AND significance check (memory analysis)
Merges results intelligently to prioritize the most relevant check-in

Supports --daily-note-mode to auto-append significant events to vault daily notes
"""

import subprocess
import sys
import json
from datetime import datetime, timedelta

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

def check_recent_conversation():
    """Check if we've recently discussed activities to avoid repetition"""
    try:
        # Simple approach: check if we've talked about running in the last few exchanges
        # by reading the session transcript directly from OpenClaw
        
        # For now, use a simpler heuristic - track when we last sent a run check-in
        # and avoid repeating within a few hours
        state_file = "/data/workspace/memory/context-check-history.json"
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}
        
        # Check when we last asked about running
        if 'last_run_checkin' in state:
            last_checkin = datetime.fromisoformat(state['last_run_checkin'])
            cutoff = datetime.now() - timedelta(hours=2)
            
            if last_checkin > cutoff:
                return {'running': True}  # We recently asked about running
        
        # If we get here, we haven't asked about running recently
        return {'running': False}
        
    except Exception as e:
        return {"conversation_unavailable": True}

def record_run_checkin():
    """Record that we just asked about running to avoid repetition"""
    try:
        state_file = "/data/workspace/memory/context-check-history.json"
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}
        
        state['last_run_checkin'] = datetime.now().isoformat()
        
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        pass  # Silently fail - this is just optimization, not critical

def merge_contexts(external_events, significance_result):
    """Merge external and significance contexts intelligently"""
    messages = []
    
    # Check conversation history to avoid repetition
    conversation_check = check_recent_conversation()
    
    # Priority 1: Recent runs (Kelly specifically called this out)
    # BUT skip if we recently discussed running
    if 'run_today' in external_events and not conversation_check.get('running', False):
        run_info = external_events['run_today']
        messages.append(f"Nice work on your run! {run_info} - how did it feel? 🏃‍♀️")
        
        # Record that we asked about running
        record_run_checkin()
        
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
        # Check conversation history even in fallback cases
        conversation_check = check_recent_conversation()
        if 'run_today' in external_events and not conversation_check.get('running', False):
            run_info = external_events['run_today']
            record_run_checkin()
            return f"Saw your run! {run_info} - how did it feel? 🏃‍♀️"
        else:
            return "Everything running smooth - how are YOU doing?"
    
    # Both successful - merge intelligently
    return merge_contexts(external_events, significance_result)

def detect_and_log_events():
    """Detect significant events and log them to daily vault note"""
    try:
        # Get both external and significance data
        external_events = run_full_context_check()
        significance_result = run_significance_check()
        
        events_logged = []
        
        # Check for external events to log
        if 'run_today' in external_events:
            # Extract run details
            run_info = external_events['run_today']
            # Parse run info: "✅ Ran today: 7.03mi at 8:42/mi"
            if "✅ Ran today:" in run_info:
                run_details = run_info.replace("✅ Ran today: ", "")
                log_content = f"Morning run completed: {run_details}, feeling strong"
                
                # Call daily-note-append.py
                result = subprocess.run([
                    'python3', '/data/workspace/scripts/daily-note-append.py', 
                    log_content, 'Health'
                ], capture_output=True, text=True, cwd='/data/workspace')
                
                if result.returncode == 0:
                    events_logged.append(f"Logged run: {run_details}")
        
        # Check for health insights
        if 'health' in external_events:
            health_info = external_events['health']
            # Only log significant health changes, not routine data
            if any(indicator in health_info for indicator in ['😴', '🥱', '💪', 'trending']):
                log_content = f"Health insight: {health_info}"
                
                result = subprocess.run([
                    'python3', '/data/workspace/scripts/daily-note-append.py', 
                    log_content, 'Health'
                ], capture_output=True, text=True, cwd='/data/workspace')
                
                if result.returncode == 0:
                    events_logged.append(f"Logged health: {health_info}")
        
        # Check for significant memory events
        if 'significance_message' in significance_result and 'big_building_day' in significance_result['significance_message']:
            # Only log actual technical work, not false positives
            log_content = "Technical work session - system improvements and fixes"
            
            result = subprocess.run([
                'python3', '/data/workspace/scripts/daily-note-append.py', 
                log_content, 'Events'
            ], capture_output=True, text=True, cwd='/data/workspace')
            
            if result.returncode == 0:
                events_logged.append("Logged technical session")
        
        # Return summary of what was logged
        if events_logged:
            return f"Daily note updated: {', '.join(events_logged)}"
        else:
            return ""  # Nothing significant to log
            
    except Exception as e:
        return f"Daily note logging error: {str(e)[:50]}"

if __name__ == "__main__":
    # Check for daily-note-mode flag
    if len(sys.argv) > 1 and '--daily-note-mode' in sys.argv:
        result = detect_and_log_events()
        if result:
            print(result)
    else:
        # Normal context check mode
        result = get_combined_context()
        if result:
            print(result)
    # If empty, print nothing (heartbeat will continue to other checks)
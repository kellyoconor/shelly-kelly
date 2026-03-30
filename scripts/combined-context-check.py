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
                
            # Check for obsidian/project data
            obsidian_lines = [l for l in output.split('\n') if l.startswith('📚 Obsidian:')]
            if obsidian_lines:
                external_events['obsidian'] = obsidian_lines[0].replace('📚 Obsidian: ', '')
                
            # Check for running status (including no run today)
            running_lines = [l for l in output.split('\n') if l.startswith('🏃‍♀️ Running:')]
            if running_lines:
                external_events['running'] = running_lines[0].replace('🏃‍♀️ Running: ', '')
            
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
        # Read session state to track what we've discussed
        session_state_file = "/data/workspace/memory/session-discussion-state.json"
        
        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            session_state = {}
        
        # Get current hour to reset discussion tracking periodically
        current_hour = datetime.now().strftime("%Y-%m-%d-%H")
        
        # Check if state has the expected structure
        if 'discussed_topics' not in session_state:
            session_state = {
                'last_hour': current_hour,
                'discussed_topics': {
                    'running': False,
                    'health_data': False,
                    'calendar': False
                }
            }
        else:
            # Reset if it's a new hour (prevents endless blocking)
            if session_state.get('last_hour') != current_hour:
                session_state['last_hour'] = current_hour
                session_state['discussed_topics'] = {
                    'running': False,
                    'health_data': False,
                    'calendar': False
                }
        
        discussed_topics = session_state.get('discussed_topics', {
            'running': False,
            'health_data': False,
            'calendar': False
        })
        
        # Fallback to timestamp check for running if session state is empty
        if not discussed_topics.get('running'):
            fallback = check_timestamp_fallback()
            discussed_topics['running'] = fallback.get('running', False)
            
        return discussed_topics
        
    except Exception as e:
        # Fallback to simpler check if session state access fails
        return check_timestamp_fallback()

def check_timestamp_fallback():
    """Fallback timestamp-based check when session history isn't available"""
    try:
        state_file = "/data/workspace/memory/context-check-history.json"
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            state = {}
        
        discussed_topics = {
            'running': False,
            'health_data': False,
            'calendar': False
        }
        
        # Check when we last asked about running
        if 'last_run_checkin' in state:
            last_checkin = datetime.fromisoformat(state['last_run_checkin'])
            cutoff = datetime.now() - timedelta(hours=2)
            
            if last_checkin > cutoff:
                discussed_topics['running'] = True
                
        return discussed_topics
        
    except Exception as e:
        return {
            'running': False,
            'health_data': False, 
            'calendar': False,
            'conversation_unavailable': True
        }

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
        
        # Also record in session state
        record_discussion_topic('running')
            
    except Exception as e:
        pass  # Silently fail - this is just optimization, not critical

def record_discussion_topic(topic):
    """Record that we discussed a specific topic in this session"""
    try:
        session_state_file = "/data/workspace/memory/session-discussion-state.json"
        
        try:
            with open(session_state_file, 'r') as f:
                session_state = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            session_state = {}
        
        # Ensure structure exists
        if 'discussed_topics' not in session_state:
            session_state['discussed_topics'] = {}
            
        session_state['discussed_topics'][topic] = True
        session_state['last_updated'] = datetime.now().isoformat()
        
        with open(session_state_file, 'w') as f:
            json.dump(session_state, f, indent=2)
            
    except Exception as e:
        pass  # Silently fail - this is just optimization, not critical

def detect_and_record_response(user_message):
    """Detect what Kelly is responding to and mark appropriate topics as discussed"""
    try:
        message_lower = user_message.lower()
        
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
            record_discussion_topic(topic)
            
        return detected_topics
        
    except Exception as e:
        return []  # Fail silently

def merge_contexts(external_events, significance_result):
    """SMART Priority Logic - prioritize most INTERESTING/ACTIONABLE context"""
    messages = []
    
    conversation_check = check_recent_conversation()
    
    # PRIORITY 1: Actionable issues that need attention
    # NOTE: Calendar auth disabled per Kelly's request - she doesn't want to deal with it
    # if ('calendar_auth' in external_events and 
    #     not conversation_check.get('calendar', False)):
    #     messages.append("Quick heads up - your calendar authentication expired. Want me to help you fix it? 📅")
    #     record_discussion_topic('calendar')
    #     return messages[0]
    
    # PRIORITY 2: Recent runs (Kelly specifically called this out) 
    if 'run_today' in external_events and not conversation_check.get('running', False):
        run_info = external_events['run_today']
        messages.append(f"Nice work on your run! {run_info} - how did it feel? 🏃‍♀️")
        record_run_checkin()
        return messages[0]
        
    # PRIORITY 3: MISSING expected activities (more interesting than health data)
    # Check if it's a weekday morning and no run yet
    from datetime import datetime
    now = datetime.now()
    if (now.weekday() < 5 and  # Weekday
        9 <= now.hour <= 12 and  # Morning window
        'run_today' not in external_events and 
        not conversation_check.get('running', False)):
        
        # Check if they ran yesterday to understand pattern
        running_context = external_events.get('running', '')
        if 'Yesterday:' in running_context:
            messages.append("No run today - taking a rest day or just haven't gotten out there yet? 🏃‍♀️")
        else:
            messages.append("No run today - how's your energy for getting out there later? 🏃‍♀️")
        record_discussion_topic('running')
        return messages[0]
    
    # PRIORITY 4: Significant emotional/personal processing
    if 'significance_message' in significance_result:
        messages.append(significance_result['significance_message'])
        return messages[0]
        
    # PRIORITY 5: Morning routine check (coffee, etc.) - but only in morning hours
    if (9 <= now.hour <= 11 and 
        not conversation_check.get('morning_routine', False)):
        messages.append("Did you get your usual Starbucks order this morning? ☕")
        record_discussion_topic('morning_routine')
        return messages[0]
    
    # PRIORITY 6: Current projects/work
    obsidian_context = external_events.get('obsidian', '')
    if ('Steely' in obsidian_context and
        not conversation_check.get('current_work', False)):
        messages.append("How's the Steely development going? Any breakthroughs today? 🤖")
        record_discussion_topic('current_work')
        return messages[0]
        
    # PRIORITY 7: Health data only if particularly notable (extreme scores)
    if ('health' in external_events and 
        not conversation_check.get('health_data', False)):
        health_msg = external_events['health']
        
        # Only mention health if scores are notably high/low or have clear emojis
        if (any(emoji in health_msg for emoji in ['💪', '🔥', '⚡', '😴', '🥱', '💤']) or
            any(num in health_msg for num in ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100']) or
            any(num in health_msg for num in ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50'])):
            
            if '😴' in health_msg or '🥱' in health_msg:
                messages.append(f"Your body's telling a story today: {health_msg}. How are you feeling energy-wise?")
            else:
                messages.append(f"Looking strong: {health_msg}. How's your energy matching the data?")
            record_discussion_topic('health_data')
            return messages[0]
        
    # PRIORITY 8: Default caring check-in (only if nothing else is interesting)
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
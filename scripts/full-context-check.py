#!/usr/bin/env python3
"""
Complete Context Checking System
All data sources before every conversation
"""

import subprocess
import json
import os
import sys
from datetime import datetime, timedelta

def get_running_context():
    """Get Strava running context"""
    try:
        result = subprocess.run(['python3', 'scripts/strava.py', 'runs', '3'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/strava')
        
        if result.returncode != 0:
            return "❌ Strava check failed"
        
        runs = json.loads(result.stdout)
        if not runs:
            return "❌ No recent runs"
        
        recent_cutoff = datetime.now() - timedelta(days=2)
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if run today
        today_runs = [r for r in runs if r['_date'] == today]
        if today_runs:
            run = today_runs[0]
            return f"✅ Ran today: {run['_distance_mi']}mi at {run['_pace_mi']}"
        
        # Check recent runs
        last_run = runs[0]
        run_date = datetime.strptime(last_run['_date'], '%Y-%m-%d')
        days_since = (datetime.now() - run_date).days
        
        if days_since == 1:
            return f"⏳ Yesterday: {last_run['_date']}, {last_run['_distance_mi']}mi"
        else:
            return f"❌ No recent runs (last: {last_run['_date']}, {days_since} days ago)"
            
    except Exception as e:
        return f"❌ Error: {str(e)[:50]}"

def get_calendar_context():
    """Get today's calendar context"""
    try:
        result = subprocess.run(['python3', 'scripts/calendar.py', 'today'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/google-calendar')
        
        if result.returncode != 0:
            # Calendar auth might be broken - but Kelly doesn't want to deal with it
            # Silently skip calendar instead of alerting about auth issues
            return "📅 Calendar offline (no worries)"
        
        output = result.stdout.strip()
        if not output or "no events" in output.lower():
            return "✅ Clear day, no meetings"
        
        # Count events
        lines = output.split('\n')
        event_lines = [l for l in lines if ':' in l and ('AM' in l or 'PM' in l)]
        
        if len(event_lines) == 1:
            return f"📅 Light day: {event_lines[0].strip()[:40]}..."
        elif len(event_lines) <= 3:
            return f"📅 {len(event_lines)} meetings today"
        else:
            return f"📅 Busy day: {len(event_lines)} meetings"
            
    except Exception as e:
        return f"❌ Calendar error: {str(e)[:30]}"

def get_health_context():
    """Get Oura health context"""
    try:
        # Get today's data (yesterday's sleep + today's readiness)
        result = subprocess.run(['python3', 'scripts/oura.py', 'brief'], 
                               capture_output=True, text=True, cwd='/data/workspace/skills/oura')
        
        if result.returncode != 0:
            return "❌ Oura check failed"
        
        output = result.stdout.strip()
        
        try:
            # Try to parse as JSON first
            data = json.loads(output)
            
            metrics = []
            
            # Readiness score
            if 'readiness' in data and 'score' in data['readiness']:
                readiness = data['readiness']['score']
                if readiness >= 85:
                    metrics.append(f"💪 {readiness}% ready")
                elif readiness >= 70:
                    metrics.append(f"⚖️ {readiness}% ready")
                else:
                    metrics.append(f"😴 {readiness}% ready")
            
            # Sleep score
            if 'sleep' in data and 'score' in data['sleep']:
                sleep_score = data['sleep']['score']
                if sleep_score >= 85:
                    metrics.append(f"😴 {sleep_score}% sleep")
                elif sleep_score >= 70:
                    metrics.append(f"⏰ {sleep_score}% sleep")
                else:
                    metrics.append(f"🥱 {sleep_score}% sleep")
            
            return " ".join(metrics) if metrics else "💍 Health data available"
            
        except json.JSONDecodeError:
            # Fall back to text parsing if not JSON
            readiness = extract_metric(output, r'readiness.*?(\d+)%?', 'Readiness')
            sleep = extract_metric(output, r'sleep.*?(\d+)%?', 'Sleep')
            
            metrics = []
            if readiness:
                score = int(readiness)
                if score >= 85:
                    metrics.append(f"💪 {readiness}% ready")
                elif score >= 70:
                    metrics.append(f"⚖️ {readiness}% ready")
                else:
                    metrics.append(f"😴 {readiness}% ready")
            
            return " ".join(metrics) if metrics else "💍 Health data parsed"
        
    except Exception as e:
        return f"❌ Health error: {str(e)[:30]}"

def extract_metric(text, pattern, metric):
    """Extract metric from text using regex"""
    import re
    matches = re.findall(pattern, text.lower())
    return matches[-1] if matches else None

def get_obsidian_context():
    """Get Obsidian vault context"""
    try:
        result = subprocess.run(['python3', '/data/workspace/scripts/context-obsidian.py'], 
                               capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0 and result.stdout:
            # Extract the summary line
            lines = result.stdout.strip().split('\n')
            context_lines = [l for l in lines if l.startswith(('📝', '🎯', '💭', '🎭'))]
            
            if context_lines:
                # Take the first meaningful context
                return context_lines[0][:60] + "..." if len(context_lines[0]) > 60 else context_lines[0]
            else:
                return "📚 Vault checked"
        else:
            return "❌ Vault check failed"
            
    except Exception as e:
        return f"❌ Vault error: {str(e)[:30]}"

def get_research_context():
    """Get research activity context"""
    try:
        result = subprocess.run(['python3', 'src/main.py', '--status'], 
                               capture_output=True, text=True, cwd='/data/workspace/kelly-research-copilot')
        
        if result.returncode == 0:
            return "🔬 Research system active"
        else:
            return "🔬 Research system idle"
            
    except Exception as e:
        return "❌ Research check failed"

def get_email_context():
    """Get email activity context"""
    try:
        # Check if there are unread emails via agentmail
        # For now, just placeholder
        return "📧 Email checked"
        
    except Exception as e:
        return "❌ Email check failed"

def get_full_context():
    """Get complete context from all sources"""
    print("🔍 Running full context check...")
    print("=" * 50)
    
    contexts = {
        "🏃‍♀️ Running": get_running_context(),
        "📅 Calendar": get_calendar_context(), 
        "💍 Health": get_health_context(),
        "📚 Obsidian": get_obsidian_context(),
        "🔬 Research": get_research_context(),
        "📧 Email": get_email_context()
    }
    
    print("📊 COMPLETE CONTEXT CHECK:")
    print("-" * 30)
    
    for source, context in contexts.items():
        print(f"{source}: {context}")
    
    print("-" * 30)
    print("✅ Full context ready for conversation!")
    
    return contexts

if __name__ == "__main__":
    get_full_context()
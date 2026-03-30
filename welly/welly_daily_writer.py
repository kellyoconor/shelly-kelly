#!/usr/bin/env python3
"""
Welly Daily Writer: Standardized way for all Welly components to write to vault

Ensures all Welly insights go to the "Welly Insights" section with consistent formatting
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def write_welly_insight(content: str, insight_type: str = "general"):
    """Write a Welly insight to today's daily note"""
    
    # Add emoji prefix based on insight type
    emoji_map = {
        'rpe': '🏃‍♀️',
        'recovery': '💪', 
        'pattern': '📈',
        'alert': '🚨',
        'health': '💍',
        'general': '💙'
    }
    
    emoji = emoji_map.get(insight_type, '💙')
    formatted_content = f"{content} {emoji}"
    
    try:
        result = subprocess.run([
            'python3', '/data/workspace/scripts/daily-note-append.py',
            formatted_content,
            'Welly Insights'
        ], capture_output=True, text=True, cwd='/data/workspace')
        
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
            
    except Exception as e:
        return False, str(e)

def log_rpe_insight(effort, legs, satisfaction, context=""):
    """Log RPE data as a Welly insight"""
    insight = f"RPE logged: Effort {effort}/10, Legs {legs}/10, Satisfaction {satisfaction}/10"
    if context:
        insight += f" ({context})"
    
    return write_welly_insight(insight, 'rpe')

def log_pattern_insight(pattern_description):
    """Log pattern detection as a Welly insight"""
    return write_welly_insight(f"Pattern detected: {pattern_description}", 'pattern')

def log_recovery_insight(recovery_description):
    """Log recovery-related insight"""
    return write_welly_insight(f"Recovery insight: {recovery_description}", 'recovery')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 welly-daily-writer.py 'insight content' [type]")
        sys.exit(1)
        
    content = sys.argv[1]
    insight_type = sys.argv[2] if len(sys.argv) > 2 else 'general'
    
    success, message = write_welly_insight(content, insight_type)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
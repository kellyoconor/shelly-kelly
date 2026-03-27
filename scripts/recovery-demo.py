#!/usr/bin/env python3
"""
Recovery Tracking Demo for Kelly

Shows how the recovery tracking system works and how to integrate it.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

def demo_recovery_system():
    """Demonstrate the recovery tracking system"""
    
    print("🔄 Kelly's Recovery Tracking System Demo")
    print("=" * 50)
    
    # Show current status
    print("\n1. Current recovery status:")
    from recovery_interface import process_recovery_message
    
    status = process_recovery_message("recovery status")
    print(status or "No recovery gaps detected")
    
    print("\n2. Recent activities:")
    recent = process_recovery_message("recent recovery") 
    print(recent or "No recent activities logged")
    
    print("\n3. How to log activities via WhatsApp:")
    examples = [
        "logged stretching 15",
        "did foam rolling",
        "had massage 60",
        "just did stretches 10"
    ]
    
    for example in examples:
        response = process_recovery_message(example)
        print(f"  '{example}' → {response}")
    
    print("\n4. Status check commands:")
    status_examples = [
        "recovery status",
        "recovery check", 
        "recent recovery"
    ]
    
    for example in status_examples:
        response = process_recovery_message(example)
        print(f"  '{example}' → Status check activated")
    
    print("\n" + "=" * 50)
    print("🎯 Integration with Shelly's heartbeat system:")
    print("- Add recovery reminder check to HEARTBEAT.md")
    print("- Welly will detect gaps and suggest recovery activities")
    print("- Kelly can log activities via WhatsApp using natural language")
    print("- System learns patterns and adjusts reminder frequency")

if __name__ == "__main__":
    # Import the recovery interface
    import sys
    sys.path.insert(0, '/data/workspace/scripts')
    
    demo_recovery_system()
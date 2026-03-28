#!/usr/bin/env python3
"""
Real-Time Event Detection for Kelly's Daily Notes

Scans recent conversation transcripts to detect significant events and automatically
append them to the daily note as they happen throughout the day.
"""

import json
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

class EventDetector:
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.state_file = self.workspace / "memory" / "event-detection-state.json"
        self.load_state()
        
    def load_state(self):
        """Load tracking state for what events have been processed"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
            else:
                self.state = {
                    "last_scan_timestamp": None,
                    "processed_events": [],
                    "today": None
                }
        except:
            self.state = {
                "last_scan_timestamp": None,
                "processed_events": [],
                "today": None
            }
    
    def save_state(self):
        """Save tracking state"""
        try:
            os.makedirs(self.state_file.parent, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except:
            pass
    
    def get_recent_session_content(self, hours_back: int = 2) -> str:
        """Get recent session transcript content for analysis"""
        try:
            # Look for main session transcript
            session_dir = Path("/data/.clawdbot/agents/main/sessions")
            if not session_dir.exists():
                return ""
            
            # Get the most recent session file
            session_files = list(session_dir.glob("*.jsonl"))
            if not session_files:
                return ""
            
            # Get the newest session file
            newest_session = max(session_files, key=lambda f: f.stat().st_mtime)
            
            # Read recent content (last few hours)
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_content = []
            
            with open(newest_session, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if 'timestamp' in entry:
                            entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                            if entry_time.replace(tzinfo=None) > cutoff_time:
                                if entry.get('role') in ['user', 'assistant'] and 'content' in entry:
                                    recent_content.append(entry['content'])
                    except:
                        continue
            
            return "\n".join(recent_content)
            
        except Exception as e:
            return ""
    
    def detect_technical_work_events(self, content: str) -> List[Dict]:
        """Detect technical work and debugging sessions"""
        events = []
        
        # Major debugging/building sessions
        tech_patterns = [
            (r"fix(?:ed|ing)? (?:the )?(.+?)(spam|bug|issue|problem)", "Fixed {}", "Work & Projects"),
            (r"built? (.+?)(system|tracking|logic|detection)", "Built {}", "Work & Projects"), 
            (r"creat(?:ed|ing) (.+?)(system|tracker|interface)", "Created {}", "Work & Projects"),
            (r"Major (.+?) overhaul", "Major {} overhaul", "Work & Projects"),
            (r"commit(?:ted|s?) (.+?)(?:\.|$)", "Committed {}", "Work & Projects")
        ]
        
        for pattern, template, category in tech_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                description = template.format(match.group(1).strip())
                if len(description) > 10:  # Avoid tiny meaningless matches
                    events.append({
                        "type": "technical_work",
                        "category": category,
                        "description": description,
                        "confidence": 0.8
                    })
        
        return events
    
    def detect_self_care_events(self, content: str) -> List[Dict]:
        """Detect self-care and wellness activities"""
        events = []
        
        # Self-care activities
        care_patterns = [
            (r"(?:had|got|went to) (?:a )?(.+?)(?:appointment|massage|spa)", "{} appointment", "Events & Activities"),
            (r"(\d+)(?:-| )?min(?:ute)? (.+?)(massage|spa|treatment)", "{} minute {}", "Events & Activities"),
            (r"(?:trying to|planning to) (.+?) every month", "Planning {} monthly", "Health & Training"),
            (r"rescue (.+?) appointment", "Rescue {} appointment", "Events & Activities")
        ]
        
        for pattern, template, category in care_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                description = template.format(*match.groups())
                events.append({
                    "type": "self_care",
                    "category": category,
                    "description": description,
                    "confidence": 0.9
                })
        
        return events
    
    def detect_emotional_events(self, content: str) -> List[Dict]:
        """Detect significant emotional processing or life events"""
        events = []
        
        # Emotional processing indicators
        emotional_indicators = [
            "feeling alone", "feeling lonely", "feeling sad", "feeling forgotten",
            "family didn't reach out", "sisters forget about me",
            "convergence moment", "heavy feeling", "sitting in it",
            "scotland kel", "choose brave"
        ]
        
        # Look for emotional content
        content_lower = content.lower()
        emotional_score = sum(1 for indicator in emotional_indicators if indicator in content_lower)
        
        if emotional_score >= 2:  # Multiple emotional indicators
            if "family" in content_lower and ("forgot" in content_lower or "alone" in content_lower):
                events.append({
                    "type": "emotional_processing", 
                    "category": "Thoughts & Reflections",
                    "description": "Processing feelings about family connection and loneliness",
                    "confidence": 0.9
                })
            elif "convergence moment" in content_lower:
                events.append({
                    "type": "emotional_processing",
                    "category": "Thoughts & Reflections", 
                    "description": "Emotional convergence moment - feeling weight of multiple stressors",
                    "confidence": 0.9
                })
        
        return events
    
    def detect_recovery_events(self, content: str) -> List[Dict]:
        """Detect recovery activities (these should already be logged by recovery system)"""
        events = []
        
        # Recovery activities - these are handled by the recovery tracker
        # but we can detect if they're mentioned in conversation
        recovery_patterns = [
            (r"logged (.+?) (\d+)", "Recovery: {} ({}min)", "Health & Training"),
            (r"did (.+?)(?:$|\.|\s)", "Recovery: {}", "Health & Training") 
        ]
        
        for pattern, template, category in recovery_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                activity = match.group(1).strip()
                if activity in ['stretching', 'foam rolling', 'massage', 'bath']:
                    # Skip - this should be handled by recovery tracker
                    continue
        
        return events
    
    def should_append_event(self, event: Dict) -> bool:
        """Check if this event should be appended to daily note"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Reset processed events for new day
        if self.state.get("today") != today:
            self.state["today"] = today
            self.state["processed_events"] = []
        
        # Create event signature for deduplication
        event_sig = f"{event['type']}_{event['category']}_{event['description'][:30]}"
        
        # Check if we've already processed this type of event today
        if event_sig in self.state["processed_events"]:
            return False
        
        # Check confidence threshold
        if event.get("confidence", 0) < 0.7:
            return False
        
        # Add to processed events
        self.state["processed_events"].append(event_sig)
        
        return True
    
    def append_to_daily_note(self, event: Dict) -> bool:
        """Append event to daily note using existing script"""
        try:
            description = event["description"]
            category = event["category"]
            
            # Use existing daily-note-append script
            result = subprocess.run([
                'python3', 
                str(self.workspace / 'scripts' / 'daily-note-append.py'),
                description,
                category
            ], capture_output=True, text=True, cwd=self.workspace)
            
            return result.returncode == 0
            
        except Exception as e:
            return False
    
    def scan_and_process_events(self) -> Dict:
        """Main function: scan recent content and process any new events"""
        results = {
            "events_detected": [],
            "events_appended": [],
            "errors": []
        }
        
        try:
            # Get recent content
            content = self.get_recent_session_content(hours_back=2)
            
            if not content:
                return results
            
            # Detect different types of events
            all_events = []
            all_events.extend(self.detect_technical_work_events(content))
            all_events.extend(self.detect_self_care_events(content))
            all_events.extend(self.detect_emotional_events(content))
            
            results["events_detected"] = all_events
            
            # Process each event
            for event in all_events:
                if self.should_append_event(event):
                    if self.append_to_daily_note(event):
                        results["events_appended"].append(event)
                    else:
                        results["errors"].append(f"Failed to append: {event['description']}")
            
            # Save state
            self.save_state()
            
        except Exception as e:
            results["errors"].append(f"Scan error: {str(e)}")
        
        return results

def main():
    """Command line interface"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verbose":
        verbose = True
    else:
        verbose = False
    
    detector = EventDetector()
    results = detector.scan_and_process_events()
    
    if verbose or results["events_appended"]:
        print("🔍 Real-time Event Detection")
        print("=" * 40)
        
        if results["events_detected"]:
            print(f"\n📋 Detected {len(results['events_detected'])} events:")
            for event in results["events_detected"]:
                conf = event.get('confidence', 0) * 100
                print(f"  • {event['description']} ({event['category']}) - {conf:.0f}%")
        
        if results["events_appended"]:
            print(f"\n✅ Appended {len(results['events_appended'])} new events to daily note:")
            for event in results["events_appended"]:
                print(f"  • {event['description']} → {event['category']}")
        
        if results["errors"]:
            print(f"\n❌ Errors:")
            for error in results["errors"]:
                print(f"  • {error}")
        
        if not results["events_detected"]:
            print("\n🔍 No significant events detected in recent conversation")
    
    # Return exit code based on whether we appended anything
    return 0 if not results["errors"] else 1

if __name__ == "__main__":
    exit(main())
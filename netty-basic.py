#!/usr/bin/env python3
"""
Netty - Gap Detector Subagent
Finds things that matter to Kelly that haven't been followed up on.
Surfaces natural check-in prompts for Shelly.

CRITICAL RULE: Netty NEVER asks Kelly directly. Feeds Shelly. Shelly does the asking.
"""

import os
import json
import re
import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import subprocess

@dataclass
class Gap:
    """Represents an unfollowed thread or gap"""
    category: str
    description: str
    days_old: int
    importance: int  # 1-10
    prompt: str
    source_file: str
    evidence: str

class NettyScanner:
    def __init__(self):
        self.workspace = Path("/data/workspace")
        self.kelly_vault = Path("/data/kelly-vault")
        self.memory_dir = self.workspace / "memory"
        self.daily_notes_dir = self.kelly_vault / "01-Daily" / "2026"
        self.log_file = self.kelly_vault / "netty_log.md"
        self.output_file = self.workspace / "pending_checkins.md"
        
        self.today = datetime.date.today()
        self.seven_days_ago = self.today - datetime.timedelta(days=7)
        
        # Pattern keywords for different gap types
        self.people_keywords = {
            'family': ['mom', 'dad', 'family', 'sister', 'brother', 'parent'],
            'friends': ['friend', 'roommate', 'buddy', 'called', 'texted'],
            'work': ['interview', 'NWSL', 'meeting', 'call', 'zoom', 'work', 'job'],
            'health': ['doctor', 'appointment', 'therapy', 'check-up', 'medical']
        }
        
        self.event_keywords = [
            'interview', 'meeting', 'appointment', 'call', 'event', 'deadline',
            'presentation', 'conference', 'party', 'dinner', 'lunch'
        ]
        
        self.stress_keywords = [
            'worried', 'anxious', 'stressed', 'concerned', 'deadline', 'pressure',
            'overwhelming', 'difficult', 'challenging', 'issue', 'problem'
        ]

    def scan_memory_files(self, days_back=7) -> List[Gap]:
        """Scan recent memory files for unfollowed patterns"""
        gaps = []
        
        # Get recent memory files
        cutoff_date = self.today - datetime.timedelta(days=days_back)
        memory_files = []
        
        for file in self.memory_dir.glob("2026-*.md"):
            try:
                date_str = file.stem  # e.g., "2026-03-11"
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if file_date >= cutoff_date:
                    memory_files.append((file, file_date))
            except ValueError:
                continue
        
        # Sort by date (newest first)
        memory_files.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze each file
        for file_path, file_date in memory_files:
            content = file_path.read_text(encoding='utf-8')
            gaps.extend(self._analyze_memory_content(content, file_path, file_date))
        
        return gaps

    def _analyze_memory_content(self, content: str, file_path: Path, file_date: datetime.date) -> List[Gap]:
        """Analyze memory file content for gaps"""
        gaps = []
        lines = content.split('\n')
        
        # Track mentions without follow-ups
        mentioned_people = set()
        mentioned_events = set()
        stress_indicators = []
        
        # Look for patterns
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Check for people mentions
            for category, keywords in self.people_keywords.items():
                for keyword in keywords:
                    if keyword in line_lower and not self._has_followup(lines, i):
                        mentioned_people.add((category, keyword, line.strip()))
            
            # Check for events
            for keyword in self.event_keywords:
                if keyword in line_lower and not self._has_followup(lines, i):
                    mentioned_events.add((keyword, line.strip()))
            
            # Check for stress/open loops
            for keyword in self.stress_keywords:
                if keyword in line_lower:
                    stress_indicators.append(line.strip())
        
        # Convert findings to gaps
        days_old = (self.today - file_date).days
        
        # People gaps
        for category, keyword, evidence in mentioned_people:
            if days_old >= 2:  # Give at least 2 days before flagging
                gaps.append(Gap(
                    category=f"people_{category}",
                    description=f"{category.title()} mention with no follow-up",
                    days_old=days_old,
                    importance=self._calculate_importance(keyword, days_old),
                    prompt=f"How are things going with {keyword}? You mentioned them {days_old} days ago.",
                    source_file=str(file_path),
                    evidence=evidence
                ))
        
        # Event gaps
        for keyword, evidence in mentioned_events:
            if days_old >= 1:  # Events need faster follow-up
                gaps.append(Gap(
                    category="events",
                    description=f"Event/meeting with no follow-up",
                    days_old=days_old,
                    importance=min(9, 6 + days_old),  # Events get more important over time
                    prompt=f"How did that {keyword} go? It was {days_old} days ago.",
                    source_file=str(file_path),
                    evidence=evidence
                ))
        
        # Stress gaps (only if old and unresolved)
        if days_old >= 3:
            for evidence in stress_indicators:
                # Extract the stress word from the evidence
                stress_word = "worried"
                for keyword in self.stress_keywords:
                    if keyword in evidence.lower():
                        stress_word = keyword
                        break
                
                gaps.append(Gap(
                    category="stress",
                    description=f"Stress/concern never revisited",
                    days_old=days_old,
                    importance=7,
                    prompt=f"How are you feeling about that thing you were {stress_word} about? Still on your mind?",
                    source_file=str(file_path),
                    evidence=evidence
                ))
        
        return gaps

    def _has_followup(self, lines: List[str], start_index: int) -> bool:
        """Check if there's a follow-up mention in the next few lines"""
        followup_keywords = ['update', 'follow', 'later', 'outcome', 'result', 'went well', 'turned out']
        
        # Check next 5 lines
        for i in range(start_index + 1, min(start_index + 6, len(lines))):
            line_lower = lines[i].lower()
            for keyword in followup_keywords:
                if keyword in line_lower:
                    return True
        return False

    def _calculate_importance(self, keyword: str, days_old: int) -> int:
        """Calculate importance score (1-10)"""
        base_score = 5
        
        # High priority keywords
        if keyword in ['interview', 'deadline', 'doctor', 'mom', 'dad']:
            base_score = 8
        elif keyword in ['meeting', 'appointment', 'friend']:
            base_score = 6
        
        # Age multiplier
        if days_old >= 5:
            base_score += 2
        elif days_old >= 3:
            base_score += 1
        
        return min(10, base_score)

    def scan_calendar_gaps(self) -> List[Gap]:
        """Scan for calendar events that passed without follow-up"""
        # TODO: Integrate with Google Calendar API
        # For now, return empty list - can be enhanced later
        return []

    def generate_checkin_prompts(self, gaps: List[Gap]) -> List[str]:
        """Generate natural check-in prompts in Shelly's voice"""
        if not gaps:
            return []
        
        # Sort gaps by importance and recency
        sorted_gaps = sorted(gaps, key=lambda g: (g.importance, -g.days_old), reverse=True)
        
        # Take top 3-5 most important gaps
        top_gaps = sorted_gaps[:5]
        
        prompts = []
        for gap in top_gaps:
            # Make prompts sound natural and caring
            prompt = gap.prompt
            
            # Add Shelly's conversational style
            if gap.category.startswith('people'):
                prompt = f"Hey! {prompt} Just thinking of you 💕"
            elif gap.category == 'events':
                prompt = f"I keep meaning to ask - {prompt.lower()} I'm curious how it went!"
            elif gap.category == 'stress':
                prompt = f"Just checking in - {prompt.lower()} 🫂"
            
            prompts.append(prompt)
        
        return prompts

    def log_scan_results(self, gaps: List[Gap], prompts: List[str], scan_type: str = "full"):
        """Log scan results to netty_log.md"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Ensure log file exists
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text("# Netty Scan Log\n\n")
        
        # Append new entry
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"## {timestamp} - {scan_type.title()} Scan\n\n")
            f.write(f"**Scanned:** Memory files (last 7 days), {len(gaps)} patterns found\n")
            f.write(f"**Gaps identified:** {len(gaps)}\n")
            f.write(f"**Prompts generated:** {len(prompts)}\n\n")
            
            if gaps:
                f.write("**Top patterns flagged:**\n")
                for gap in sorted(gaps, key=lambda g: g.importance, reverse=True)[:3]:
                    f.write(f"- {gap.category}: {gap.description} ({gap.days_old} days old, importance {gap.importance})\n")
                f.write("\n")
            
            if prompts:
                f.write("**Check-in prompts generated:**\n")
                for i, prompt in enumerate(prompts, 1):
                    f.write(f"{i}. {prompt}\n")
                f.write("\n")
            
            f.write("---\n\n")

    def save_pending_checkins(self, prompts: List[str]):
        """Save check-in prompts for Shelly to read"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"# Pending Check-ins\n\n"
        content += f"*Generated by Netty on {timestamp}*\n\n"
        
        if prompts:
            content += "Shelly - here are some natural check-in opportunities I found:\n\n"
            for i, prompt in enumerate(prompts, 1):
                content += f"**{i}.** {prompt}\n\n"
            content += "*Pick the most relevant one for your next heartbeat check-in.*\n"
        else:
            content += "No significant gaps found right now. Kelly seems to be following up well on things! 🎉\n"
        
        self.output_file.write_text(content, encoding='utf-8')

    def run_scan(self, scan_type: str = "full") -> Dict:
        """Run the gap detection scan"""
        print(f"🔍 Netty starting {scan_type} scan...")
        
        # Scan memory files
        memory_gaps = self.scan_memory_files(days_back=7 if scan_type == "full" else 3)
        
        # Scan calendar (placeholder for now)
        calendar_gaps = self.scan_calendar_gaps()
        
        # Combine all gaps
        all_gaps = memory_gaps + calendar_gaps
        
        # Generate prompts
        prompts = self.generate_checkin_prompts(all_gaps)
        
        # Log results
        self.log_scan_results(all_gaps, prompts, scan_type)
        
        # Save prompts for Shelly
        self.save_pending_checkins(prompts)
        
        print(f"✅ Netty scan complete: {len(all_gaps)} gaps found, {len(prompts)} prompts generated")
        
        return {
            'gaps_found': len(all_gaps),
            'prompts_generated': len(prompts),
            'top_gaps': [g.description for g in sorted(all_gaps, key=lambda x: x.importance, reverse=True)[:3]]
        }

def main():
    scanner = NettyScanner()
    
    # Determine scan type from command line arg
    import sys
    scan_type = "light" if len(sys.argv) > 1 and sys.argv[1] == "light" else "full"
    
    # Run scan
    results = scanner.run_scan(scan_type)
    
    # Output for cron/logging
    print(json.dumps(results))

if __name__ == "__main__":
    main()
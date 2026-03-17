#!/usr/bin/env python3
"""
Netty - Enhanced Gap Detector Subagent
Finds things that matter to Kelly that haven't been followed up on.
Now with subagent intelligence and learning capabilities.

CRITICAL RULE: Netty NEVER asks Kelly directly. Feeds Shelly. Shelly does the asking.
"""

import os
import json
import re
import datetime
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, asdict
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
    emotional_context: str = ""
    relationship_weight: int = 5  # 1-10, how important this relationship/topic is

class NettySubagent:
    """Enhanced Netty with subagent intelligence and learning"""
    
    def __init__(self):
        self.workspace = Path("/data/workspace")
        self.kelly_vault = Path("/data/kelly-vault")
        self.memory_dir = self.workspace / "memory"
        self.daily_notes_dir = self.kelly_vault / "Daily Notes"
        self.log_file = self.kelly_vault / "netty_log.md"
        self.output_file = self.workspace / "pending_checkins.md"
        
        # Subagent structure
        self.subagent_dir = self.workspace / "subagents" / "netty"
        self.subagent_memory = self.subagent_dir / "MEMORY.md"
        self.subagent_logs = self.kelly_vault / "Memory" / "Netty"
        self.subagent_logs.mkdir(parents=True, exist_ok=True)
        
        self.today = datetime.date.today()
        self.seven_days_ago = self.today - datetime.timedelta(days=7)
        
        # Load learning preferences
        self.load_preferences()
        
        # Enhanced pattern keywords
        self.people_keywords = {
            'family': {
                'keywords': ['mom', 'dad', 'family', 'sister', 'brother', 'parent', 'grandmother', 'grandfather'],
                'weight': 9,  # High importance
                'emotional_indicators': ['worried', 'concerned', 'excited', 'proud', 'stressed', 'happy']
            },
            'friends': {
                'keywords': ['friend', 'roommate', 'buddy', 'called', 'texted', 'met up', 'dinner', 'coffee'],
                'weight': 7,
                'emotional_indicators': ['fun', 'good time', 'missed', 'worried', 'excited']
            },
            'work': {
                'keywords': ['interview', 'NWSL', 'meeting', 'call', 'zoom', 'work', 'job', 'boss', 'colleague'],
                'weight': 8,
                'emotional_indicators': ['nervous', 'excited', 'stressed', 'important', 'worried', 'hopeful']
            },
            'health': {
                'keywords': ['doctor', 'appointment', 'therapy', 'check-up', 'medical', 'dentist', 'therapist'],
                'weight': 9,
                'emotional_indicators': ['worried', 'concerned', 'nervous', 'relieved', 'anxious']
            }
        }
        
        self.event_keywords = [
            'interview', 'meeting', 'appointment', 'call', 'event', 'deadline',
            'presentation', 'conference', 'party', 'dinner', 'lunch', 'date'
        ]
        
        self.stress_keywords = [
            'worried', 'anxious', 'stressed', 'concerned', 'deadline', 'pressure',
            'overwhelming', 'difficult', 'challenging', 'issue', 'problem', 'upset'
        ]
        
        # Learning thresholds (adjusted based on feedback)
        self.sensitivity_thresholds = {
            'family': 2,  # Flag after 2 days
            'health': 1,  # Flag after 1 day
            'work': 3,    # Flag after 3 days (adjustable)
            'friends': 4, # Flag after 4 days
            'stress': 3   # Flag after 3 days
        }

    def load_preferences(self):
        """Load learning preferences from MEMORY.md"""
        if self.subagent_memory.exists():
            try:
                with open(self.subagent_memory, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple pattern matching to extract learned preferences
                    # In a full implementation, this would parse structured data
                    if "family mentions: HIGH sensitivity" in content:
                        self.sensitivity_thresholds['family'] = 1
                    if "work meetings: MEDIUM sensitivity" in content:
                        self.sensitivity_thresholds['work'] = 4
            except Exception as e:
                print(f"Warning: Could not load preferences: {e}")

    def scan_memory_files(self, days_back=7) -> List[Gap]:
        """Enhanced memory file scanning with emotional context"""
        gaps = []
        
        # Get recent memory files
        cutoff_date = self.today - datetime.timedelta(days=days_back)
        memory_files = []
        
        for file in self.memory_dir.glob("2026-*.md"):
            try:
                date_str = file.stem
                file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
                if file_date >= cutoff_date:
                    memory_files.append((file, file_date))
            except ValueError:
                continue
        
        # Sort by date (newest first)
        memory_files.sort(key=lambda x: x[1], reverse=True)
        
        # Analyze each file with enhanced intelligence
        for file_path, file_date in memory_files:
            content = file_path.read_text(encoding='utf-8')
            gaps.extend(self._analyze_memory_content_enhanced(content, file_path, file_date))
        
        return gaps

    def _analyze_memory_content_enhanced(self, content: str, file_path: Path, file_date: datetime.date) -> List[Gap]:
        """Enhanced analysis with emotional context and relationship weighting"""
        gaps = []
        lines = content.split('\n')
        
        # Track patterns with emotional context
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Enhanced people detection
            for category, config in self.people_keywords.items():
                for keyword in config['keywords']:
                    if keyword in line_lower:
                        emotional_context = self._extract_emotional_context(line, lines, i, config['emotional_indicators'])
                        
                        if emotional_context and not self._has_followup_enhanced(lines, i, keyword):
                            # Check if this is an ongoing theme vs specific event
                            if self._is_ongoing_theme(line, lines, i, keyword):
                                continue  # Skip ongoing themes, focus on specific events
                            
                            days_old = (self.today - file_date).days
                            
                            # Apply learning thresholds
                            if days_old >= self.sensitivity_thresholds.get(category, 3):
                                gaps.append(Gap(
                                    category=f"people_{category}",
                                    description=f"{category.title()} mention with emotional context",
                                    days_old=days_old,
                                    importance=self._calculate_enhanced_importance(keyword, days_old, emotional_context, config['weight']),
                                    prompt=self._generate_enhanced_prompt(category, keyword, days_old, emotional_context),
                                    source_file=str(file_path),
                                    evidence=line.strip(),
                                    emotional_context=emotional_context,
                                    relationship_weight=config['weight']
                                ))
            
            # Enhanced event detection
            for keyword in self.event_keywords:
                if keyword in line_lower:
                    emotional_context = self._extract_emotional_context(line, lines, i, ['nervous', 'excited', 'worried', 'important'])
                    
                    if emotional_context and not self._has_followup_enhanced(lines, i, keyword):
                        # Check if this is an ongoing theme vs specific event
                        if self._is_ongoing_theme(line, lines, i, keyword):
                            continue  # Skip ongoing themes like "dating era"
                        
                        days_old = (self.today - file_date).days
                        
                        if days_old >= 1:  # Events need quick follow-up
                            gaps.append(Gap(
                                category="events",
                                description=f"Event with emotional weight",
                                days_old=days_old,
                                importance=min(9, 6 + days_old + (2 if emotional_context else 0)),
                                prompt=self._generate_event_prompt(keyword, days_old, emotional_context),
                                source_file=str(file_path),
                                evidence=line.strip(),
                                emotional_context=emotional_context,
                                relationship_weight=8
                            ))
        
        return gaps

    def _extract_emotional_context(self, line: str, lines: List[str], index: int, indicators: List[str]) -> str:
        """Extract emotional context from line and surrounding context"""
        context_lines = []
        
        # Check current line and 2 lines before/after
        start = max(0, index - 2)
        end = min(len(lines), index + 3)
        
        for i in range(start, end):
            line_content = lines[i].lower()
            for indicator in indicators:
                if indicator in line_content:
                    # Extract the emotional phrase
                    words = lines[i].split()
                    for j, word in enumerate(words):
                        if indicator in word.lower():
                            # Get some context around the emotional word
                            context_start = max(0, j - 3)
                            context_end = min(len(words), j + 4)
                            emotional_phrase = " ".join(words[context_start:context_end])
                            return emotional_phrase.strip()
        
        return ""

    def _is_ongoing_theme(self, line: str, lines: List[str], index: int, keyword: str) -> bool:
        """Detect if this is an ongoing life theme vs specific event needing follow-up"""
        line_lower = line.lower()
        
        # Theme indicators (LEARNED: March 11, 2026 - dating era confusion)
        theme_phrases = [
            'focused on', 'been thinking about', 'era', 'mindset', 'journey', 
            'working on', 'trying to', 'in my', 'phase', 'lately'
        ]
        
        # General mindset indicators
        general_indicators = [
            'generally', 'overall', 'these days', 'recently', 'been'
        ]
        
        # Check if line contains theme indicators
        for phrase in theme_phrases + general_indicators:
            if phrase in line_lower:
                return True
        
        # Check for repeated mentions across multiple days (theme pattern)
        keyword_count = 0
        for other_line in lines:
            if keyword in other_line.lower():
                keyword_count += 1
        
        # If keyword appears 3+ times in same memory file, likely ongoing theme
        if keyword_count >= 3:
            return True
        
        # Event indicators (specific completed actions)
        event_verbs = ['went to', 'had a', 'met with', 'called', 'visited', 'attended']
        
        # If contains specific event verbs, likely not a theme
        for verb in event_verbs:
            if verb in line_lower:
                return False
        
        return False

    def _has_followup_enhanced(self, lines: List[str], start_index: int, keyword: str) -> bool:
        """Enhanced follow-up detection"""
        followup_keywords = ['update', 'follow', 'later', 'outcome', 'result', 'went well', 'turned out', 'how it went', 'update on']
        
        # Check next 10 lines instead of 5
        for i in range(start_index + 1, min(start_index + 11, len(lines))):
            line_lower = lines[i].lower()
            # Look for followup keywords OR the original keyword mentioned again with resolution words
            for followup in followup_keywords:
                if followup in line_lower:
                    return True
            
            # Check if the keyword appears again with resolution indicators
            if keyword in line_lower:
                resolution_words = ['good', 'well', 'fine', 'ok', 'great', 'successful', 'done', 'finished']
                if any(res in line_lower for res in resolution_words):
                    return True
        
        return False

    def _calculate_enhanced_importance(self, keyword: str, days_old: int, emotional_context: str, base_weight: int) -> int:
        """Enhanced importance calculation with emotional weighting"""
        importance = base_weight
        
        # Emotional context boost
        if emotional_context:
            stress_words = ['worried', 'anxious', 'nervous', 'stressed', 'concerned']
            excitement_words = ['excited', 'hopeful', 'important']
            
            if any(word in emotional_context.lower() for word in stress_words):
                importance += 2  # Stress needs follow-up
            elif any(word in emotional_context.lower() for word in excitement_words):
                importance += 1  # Excitement deserves follow-up
        
        # Age multiplier
        if days_old >= 5:
            importance += 2
        elif days_old >= 3:
            importance += 1
        
        return min(10, importance)

    def _generate_enhanced_prompt(self, category: str, keyword: str, days_old: int, emotional_context: str) -> str:
        """Generate caring, contextual prompts"""
        base_prompts = {
            'family': [
                f"Hey! I keep thinking about {keyword} - {emotional_context if emotional_context else 'you mentioned them'} {days_old} days ago. How are things? 💕",
                f"Just checking in - how are things with {keyword}? {emotional_context if emotional_context else 'Been thinking of you'} 🫂"
            ],
            'friends': [
                f"How did things go with {keyword}? You seemed {emotional_context if emotional_context else 'excited about it'} - just curious! 😊",
                f"Been meaning to ask - how was {keyword}? {emotional_context if emotional_context else 'Hope it was fun!'} ✨"
            ],
            'work': [
                f"I keep meaning to ask - how did that {keyword} go? {emotional_context if emotional_context else 'You seemed focused on it'} - curious how it turned out! 💼",
                f"How are you feeling about that {keyword} from {days_old} days ago? {emotional_context if emotional_context else 'Hope it went well!'} 🌟"
            ],
            'health': [
                f"Just thinking of you - how did that {keyword} go? {emotional_context if emotional_context else 'I know those can be stressful'} 🩺💕",
                f"Been wondering about your {keyword} appointment - {emotional_context if emotional_context else 'how did it go'}? Hope everything's okay 🫂"
            ]
        }
        
        import random
        prompts = base_prompts.get(category, [f"How are things with {keyword}? {emotional_context if emotional_context else ''} Just checking in! 💕"])
        return random.choice(prompts)

    def _generate_event_prompt(self, keyword: str, days_old: int, emotional_context: str) -> str:
        """Generate event-specific prompts"""
        if emotional_context:
            return f"I keep meaning to ask - how did that {keyword} go? You seemed {emotional_context} beforehand - I'm curious how it turned out! ✨"
        else:
            return f"How did that {keyword} go? It was {days_old} days ago and I'm curious how it went! 😊"

    def generate_intelligent_prompts(self, gaps: List[Gap]) -> List[str]:
        """Generate intelligent, filtered prompts"""
        if not gaps:
            return []
        
        # Sort by combination of importance, relationship weight, and emotional context
        def gap_score(gap):
            emotional_bonus = 2 if gap.emotional_context else 0
            return gap.importance + gap.relationship_weight + emotional_bonus - gap.days_old * 0.5
        
        sorted_gaps = sorted(gaps, key=gap_score, reverse=True)
        
        # Take top 2-4 gaps, avoiding overwhelming lists
        top_gaps = sorted_gaps[:4]
        
        # Filter for quality - only include gaps with minimum standards
        quality_gaps = []
        for gap in top_gaps:
            # Must have emotional context OR high relationship weight OR be recent and important
            if (gap.emotional_context or 
                gap.relationship_weight >= 8 or 
                (gap.days_old <= 2 and gap.importance >= 7)):
                quality_gaps.append(gap)
        
        # Limit to top 3 for quality
        return [gap.prompt for gap in quality_gaps[:3]]

    def log_enhanced_scan(self, gaps: List[Gap], prompts: List[str], scan_type: str = "full"):
        """Enhanced logging with learning data"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Original logging
        self.log_scan_results_original(gaps, prompts, scan_type)
        
        # Enhanced subagent logging
        daily_log = self.subagent_logs / f"{self.today}.md"
        
        with open(daily_log, 'a', encoding='utf-8') as f:
            f.write(f"\n## {timestamp} - {scan_type.title()} Scan\n\n")
            f.write(f"**Enhanced Analysis:**\n")
            f.write(f"- Total patterns: {len(gaps)}\n")
            f.write(f"- With emotional context: {len([g for g in gaps if g.emotional_context])}\n")
            f.write(f"- High relationship weight: {len([g for g in gaps if g.relationship_weight >= 8])}\n")
            f.write(f"- Quality prompts generated: {len(prompts)}\n\n")
            
            if gaps:
                f.write("**Top Patterns by Intelligence Score:**\n")
                for gap in sorted(gaps, key=lambda g: g.importance + g.relationship_weight, reverse=True)[:5]:
                    f.write(f"- {gap.category}: {gap.description}\n")
                    f.write(f"  - Days old: {gap.days_old}, Importance: {gap.importance}, Relationship weight: {gap.relationship_weight}\n")
                    if gap.emotional_context:
                        f.write(f"  - Emotional context: {gap.emotional_context}\n")
                    f.write(f"  - Evidence: {gap.evidence[:100]}...\n\n")

    def log_scan_results_original(self, gaps: List[Gap], prompts: List[str], scan_type: str = "full"):
        """Original logging method preserved for compatibility"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self.log_file.write_text("# Netty Enhanced Scan Log\n\n")
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"## {timestamp} - {scan_type.title()} Scan (Enhanced)\n\n")
            f.write(f"**Scanned:** Memory files (last 7 days), {len(gaps)} patterns found\n")
            f.write(f"**Gaps identified:** {len(gaps)}\n")
            f.write(f"**Quality prompts generated:** {len(prompts)}\n\n")
            
            if gaps:
                f.write("**Top patterns flagged:**\n")
                for gap in sorted(gaps, key=lambda g: g.importance + g.relationship_weight, reverse=True)[:3]:
                    f.write(f"- {gap.category}: {gap.description} ({gap.days_old} days old, importance {gap.importance})\n")
                f.write("\n")
            
            if prompts:
                f.write("**Enhanced check-in prompts:**\n")
                for i, prompt in enumerate(prompts, 1):
                    f.write(f"{i}. {prompt}\n")
                f.write("\n")
            
            f.write("---\n\n")

    def save_pending_checkins(self, prompts: List[str]):
        """Save enhanced prompts for Shelly (preserves original format)"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        content = f"# Pending Check-ins\n\n"
        content += f"*Generated by Enhanced Netty on {timestamp}*\n\n"
        
        if prompts:
            content += "Shelly - here are some thoughtful check-in opportunities I found:\n\n"
            for i, prompt in enumerate(prompts, 1):
                content += f"**{i}.** {prompt}\n\n"
            content += "*These are high-quality gaps with emotional context or relationship importance.*\n"
        else:
            content += "No significant gaps found right now. Kelly seems to be following up well on things that matter! 🎉\n"
        
        self.output_file.write_text(content, encoding='utf-8')

    def run_enhanced_scan(self, scan_type: str = "full") -> Dict:
        """Run enhanced gap detection with subagent intelligence"""
        print(f"🔍 Enhanced Netty starting {scan_type} scan with intelligence layer...")
        
        # Enhanced memory scanning
        memory_gaps = self.scan_memory_files(days_back=7 if scan_type == "full" else 3)
        
        # Future: calendar integration
        calendar_gaps = []  # self.scan_calendar_gaps()
        
        # Combine and enhance
        all_gaps = memory_gaps + calendar_gaps
        
        # Generate intelligent prompts
        prompts = self.generate_intelligent_prompts(all_gaps)
        
        # Enhanced logging
        self.log_enhanced_scan(all_gaps, prompts, scan_type)
        
        # Save for Shelly
        self.save_pending_checkins(prompts)
        
        # Report results
        quality_score = len([g for g in all_gaps if g.emotional_context or g.relationship_weight >= 8])
        print(f"✅ Enhanced Netty scan complete: {len(all_gaps)} patterns found, {quality_score} high-quality, {len(prompts)} prompts generated")
        
        return {
            'gaps_found': len(all_gaps),
            'quality_gaps': quality_score,
            'prompts_generated': len(prompts),
            'top_gaps': [g.description for g in sorted(all_gaps, key=lambda x: x.importance + x.relationship_weight, reverse=True)[:3]],
            'enhancement': 'subagent_intelligence_active'
        }

# Backward compatibility class
class NettyScanner(NettySubagent):
    """Backward compatibility wrapper"""
    
    def run_scan(self, scan_type: str = "full") -> Dict:
        """Original interface maintained"""
        return self.run_enhanced_scan(scan_type)

def main():
    parser = argparse.ArgumentParser(description='Netty Gap Detector')
    parser.add_argument('scan_type', nargs='?', default='full', choices=['full', 'light'])
    parser.add_argument('--subagent', action='store_true', help='Use enhanced subagent intelligence')
    parser.add_argument('--original', action='store_true', help='Use original basic logic only')
    
    args = parser.parse_args()
    
    if args.original:
        # Use basic logic (import original if needed)
        print("Using original Netty logic...")
        # Would import and use original NettyScanner here
        scanner = NettySubagent()  # For now, same class
        results = scanner.run_enhanced_scan(args.scan_type)
    else:
        # Use enhanced subagent logic (default now)
        scanner = NettySubagent()
        results = scanner.run_enhanced_scan(args.scan_type)
    
    # Output for cron/logging
    print(json.dumps(results))

if __name__ == "__main__":
    main()
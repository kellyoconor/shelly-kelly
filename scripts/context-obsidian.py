#!/usr/bin/env python3
"""
Obsidian Vault Context Checker
Parse recent daily notes, projects, and decision patterns
"""

import os
import glob
import re
from datetime import datetime, timedelta

def get_obsidian_context(days_back=3):
    """Extract relevant context from Obsidian vault"""
    vault_path = "/data/kelly-vault"
    
    context = {
        "recent_topics": [],
        "active_projects": [],
        "decisions": [],
        "mood_indicators": []
    }
    
    # Check recent daily notes
    recent_cutoff = datetime.now() - timedelta(days=days_back)
    
    # Daily Notes pattern
    daily_notes_path = f"{vault_path}/Daily Notes"
    if os.path.exists(daily_notes_path):
        for note_file in glob.glob(f"{daily_notes_path}/*.md"):
            try:
                filename = os.path.basename(note_file)
                date_match = re.match(r"(\d{4}-\d{2}-\d{2})\.md", filename)
                if not date_match:
                    continue
                
                file_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
                if file_date < recent_cutoff:
                    continue
                
                with open(note_file, 'r') as f:
                    content = f.read()
                
                # Extract topics and themes
                context["recent_topics"].extend(extract_topics(content, file_date))
                context["decisions"].extend(extract_decisions(content, file_date))
                context["mood_indicators"].extend(extract_mood(content, file_date))
                
            except Exception as e:
                continue
    
    # Check for active projects (02-Projects folder)
    projects_path = f"{vault_path}/02-Projects"
    if os.path.exists(projects_path):
        for project_file in glob.glob(f"{projects_path}/**/*.md", recursive=True):
            try:
                # Look for recently modified projects
                mod_time = datetime.fromtimestamp(os.path.getmtime(project_file))
                if mod_time >= recent_cutoff:
                    project_name = os.path.basename(project_file).replace('.md', '')
                    context["active_projects"].append({
                        "name": project_name,
                        "last_modified": mod_time.strftime("%Y-%m-%d")
                    })
            except Exception as e:
                continue
    
    return context

def extract_topics(content, date):
    """Extract mentioned topics and themes"""
    topics = []
    
    # Look for topic patterns
    patterns = [
        r"thinking about (.+?)[\.\n]",
        r"working on (.+?)[\.\n]", 
        r"researching (.+?)[\.\n]",
        r"focusing on (.+?)[\.\n]"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content.lower(), re.IGNORECASE)
        for match in matches:
            topics.append({
                "topic": match.strip(),
                "date": date.strftime("%Y-%m-%d")
            })
    
    return topics[:3]  # Limit to top 3 per day

def extract_decisions(content, date):
    """Extract decision mentions"""
    decisions = []
    
    patterns = [
        r"decided to (.+?)[\.\n]",
        r"chose to (.+?)[\.\n]",
        r"going to (.+?)[\.\n]"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content.lower(), re.IGNORECASE)
        for match in matches:
            decisions.append({
                "decision": match.strip(),
                "date": date.strftime("%Y-%m-%d")
            })
    
    return decisions[:2]  # Limit to top 2 per day

def extract_mood(content, date):
    """Extract mood and energy indicators"""
    mood_words = []
    
    # Positive indicators
    positive = ["excited", "energized", "happy", "confident", "motivated", "clear", "focused"]
    # Negative indicators  
    negative = ["frustrated", "tired", "overwhelmed", "stressed", "anxious", "unclear"]
    
    content_lower = content.lower()
    
    for word in positive + negative:
        if word in content_lower:
            mood_words.append({
                "indicator": word,
                "type": "positive" if word in positive else "negative",
                "date": date.strftime("%Y-%m-%d")
            })
    
    return mood_words[:2]  # Limit results

def format_obsidian_context(context):
    """Format context for display"""
    lines = []
    
    # Recent topics
    if context["recent_topics"]:
        topics = [f"{t['topic']}" for t in context["recent_topics"][:3]]
        lines.append(f"📝 Recent focus: {', '.join(topics)}")
    
    # Active projects
    if context["active_projects"]:
        projects = [p["name"] for p in context["active_projects"][:2]]
        lines.append(f"🎯 Active projects: {', '.join(projects)}")
    
    # Recent decisions
    if context["decisions"]:
        decision = context["decisions"][0]["decision"]
        lines.append(f"💭 Recent decision: {decision}")
    
    # Mood indicators
    if context["mood_indicators"]:
        moods = [m["indicator"] for m in context["mood_indicators"][:2]]
        lines.append(f"🎭 Recent mood: {', '.join(moods)}")
    
    return "\n".join(lines) if lines else "📝 No recent Obsidian activity"

if __name__ == "__main__":
    context = get_obsidian_context()
    print("📚 OBSIDIAN VAULT CONTEXT:")
    print("=" * 40)
    print(format_obsidian_context(context))
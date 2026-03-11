#!/usr/bin/env python3
"""
MEMORY.md management system
Keeps working memory lean while preserving important context
"""
import os
import re
from datetime import datetime, timedelta

MEMORY_FILE = "/data/workspace/MEMORY.md"
ARCHIVE_DIR = "/data/kelly-vault/Archives/memory"
VAULT_DIR = "/data/kelly-vault"

def ensure_dirs():
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

def get_memory_size():
    """Get current MEMORY.md size in characters"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return len(f.read())
    return 0

def archive_section(section_name, content):
    """Archive a section to the vault"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"{section_name.lower().replace(' ', '-')}-{timestamp}.md"
    path = os.path.join(ARCHIVE_DIR, filename)
    
    with open(path, 'w') as f:
        f.write(f"# {section_name} (Archived {timestamp})\n\n")
        f.write(content)
    
    print(f"📚 Archived '{section_name}' to {path}")
    return path

def memory_audit():
    """Analyze current MEMORY.md structure and suggest optimizations"""
    if not os.path.exists(MEMORY_FILE):
        print("❌ MEMORY.md not found")
        return
    
    with open(MEMORY_FILE, 'r') as f:
        content = f.read()
    
    size = len(content)
    lines = content.split('\n')
    
    print(f"📊 MEMORY.md Analysis:")
    print(f"   Size: {size:,} characters")
    print(f"   Lines: {len(lines)}")
    
    # Analyze sections
    sections = {}
    current_section = "header"
    current_content = []
    
    for line in lines:
        if line.startswith('##'):
            # Save previous section
            if current_content:
                sections[current_section] = '\n'.join(current_content)
            
            # Start new section
            current_section = line.strip('# ').strip()
            current_content = [line]
        else:
            current_content.append(line)
    
    # Don't forget last section
    if current_content:
        sections[current_section] = '\n'.join(current_content)
    
    print(f"\n📝 Sections:")
    for name, content in sections.items():
        char_count = len(content)
        line_count = len(content.split('\n'))
        print(f"   {name}: {char_count:,} chars, {line_count} lines")
    
    # Suggestions
    print(f"\n💡 Optimization Suggestions:")
    
    # Check for bloated sections
    for name, content in sections.items():
        if len(content) > 1000 and name not in ['Kelly', 'Me (Shelly 🐚)']:
            print(f"   🔥 '{name}' is large ({len(content):,} chars) - candidate for archiving")
    
    # Check for outdated context
    today = datetime.now()
    if '2025' in content and today.year >= 2026:
        print(f"   📅 Found 2025 references - might be outdated")
    
    # Check for redundancy
    lesson_lines = [line for line in lines if 'lesson' in line.lower() or 'learned' in line.lower()]
    if len(lesson_lines) > 10:
        print(f"   📚 Many lesson entries ({len(lesson_lines)}) - consider consolidating")

def apply_memory_rules():
    """Apply memory management rules to optimize MEMORY.md"""
    print("🧠 Applying memory management rules...")
    
    if not os.path.exists(MEMORY_FILE):
        print("❌ MEMORY.md not found")
        return
    
    # Backup current version
    backup_path = f"{MEMORY_FILE}.backup-{int(datetime.now().timestamp())}"
    os.system(f"cp {MEMORY_FILE} {backup_path}")
    print(f"💾 Backup created: {backup_path}")
    
    with open(MEMORY_FILE, 'r') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Rule 1: Archive lessons older than 6 months
    # This is a simplified version - in practice you'd want more sophisticated parsing
    
    # Rule 2: Limit "Recent Lessons" to last 10 entries
    # (This would need more sophisticated implementation)
    
    # For now, just provide analysis
    memory_audit()
    
    print(f"\n✅ Analysis complete. Manual review recommended.")
    print(f"   Original size: {original_size:,} characters")
    
    return backup_path

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 memory-manager.py [audit|optimize]")
        print("  audit    - Analyze current MEMORY.md structure")
        print("  optimize - Apply memory management rules")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "audit":
        memory_audit()
    elif command == "optimize":
        apply_memory_rules()
    else:
        print(f"Unknown command: {command}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
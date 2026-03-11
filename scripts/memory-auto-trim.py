#!/usr/bin/env python3
"""
Auto-trim MEMORY.md when it hits warning/critical levels
Archives to vault and leaves references
"""
import os
import re
from datetime import datetime

MEMORY_FILE = "/data/workspace/MEMORY.md"
VAULT_ARCHIVE = "/data/kelly-vault/Archives/memory"
MEMORY_INDEX = "/data/kelly-vault/Archives/MEMORY-INDEX.md"

def ensure_dirs():
    os.makedirs(VAULT_ARCHIVE, exist_ok=True)
    os.makedirs(os.path.dirname(MEMORY_INDEX), exist_ok=True)

def get_memory_size():
    """Get current MEMORY.md size"""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            return len(f.read())
    return 0

def parse_sections(content):
    """Parse MEMORY.md into sections"""
    sections = {}
    lines = content.split('\n')
    current_section = "header"
    current_content = []
    
    for line in lines:
        if line.startswith('## '):
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
    
    return sections

def archive_section(section_name, content, reason="size"):
    """Archive a section and return reference"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    safe_name = re.sub(r'[^\w\s-]', '', section_name).strip().replace(' ', '-').lower()
    filename = f"{safe_name}-{timestamp}.md"
    archive_path = os.path.join(VAULT_ARCHIVE, filename)
    
    # Write archived section
    with open(archive_path, 'w') as f:
        f.write(f"# {section_name} (Archived {timestamp})\n\n")
        f.write(f"*Archived from MEMORY.md due to: {reason}*\n\n")
        f.write(content)
    
    # Update index
    update_memory_index(section_name, filename, reason)
    
    # Return obsidian-style reference
    relative_path = f"Archives/memory/{filename}"
    return f"→ [[{relative_path}|{section_name} Archive]]"

def update_memory_index(section_name, filename, reason):
    """Update the master index of archived content"""
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    entry = f"- **{timestamp}** — {section_name} → `{filename}` (reason: {reason})\n"
    
    # Create or append to index
    if os.path.exists(MEMORY_INDEX):
        with open(MEMORY_INDEX, 'r') as f:
            content = f.read()
    else:
        content = "# Memory Archive Index\n\nComplete history of what was archived from MEMORY.md:\n\n"
    
    # Add new entry after header
    lines = content.split('\n')
    header_end = 3  # After title and description
    lines.insert(header_end, entry.rstrip())
    
    with open(MEMORY_INDEX, 'w') as f:
        f.write('\n'.join(lines))

def auto_trim_memory():
    """Auto-trim MEMORY.md based on size thresholds"""
    ensure_dirs()
    
    if not os.path.exists(MEMORY_FILE):
        print("❌ MEMORY.md not found")
        return False
    
    with open(MEMORY_FILE, 'r') as f:
        content = f.read()
    
    original_size = len(content)
    print(f"📊 Current MEMORY.md size: {original_size:,} chars")
    
    # Check thresholds
    if original_size < 3000:
        print("✅ Size OK, no trimming needed")
        return False
    
    # Parse sections
    sections = parse_sections(content)
    
    # Create full backup first
    backup_filename = f"MEMORY-full-{datetime.now().strftime('%Y-%m-%d-%H%M')}.md"
    backup_path = os.path.join(VAULT_ARCHIVE, backup_filename)
    with open(backup_path, 'w') as f:
        f.write(content)
    print(f"💾 Full backup: {backup_path}")
    
    # Determine what to archive
    archived_refs = []
    kept_sections = {}
    
    # Always keep core sections
    core_sections = ['Kelly', 'Me (Shelly 🐚)', 'Core Principles', 'Morning Mantras']
    
    for section_name, section_content in sections.items():
        section_size = len(section_content)
        
        # Keep core sections always
        if any(core in section_name for core in core_sections):
            kept_sections[section_name] = section_content
            print(f"✅ Keeping core section: {section_name} ({section_size} chars)")
            continue
        
        # Archive large sections or old lessons
        should_archive = False
        reason = ""
        
        if section_size > 1000:
            should_archive = True
            reason = f"large section ({section_size} chars)"
        elif "lesson" in section_name.lower() and original_size > 4000:
            should_archive = True  
            reason = "critical size + lessons"
        elif original_size > 4000 and section_name not in ['Current Context', 'Critical Automation']:
            should_archive = True
            reason = "critical size"
        
        if should_archive:
            ref = archive_section(section_name, section_content, reason)
            archived_refs.append(ref)
            print(f"🗄️  Archived: {section_name} → {reason}")
        else:
            kept_sections[section_name] = section_content
            print(f"✅ Keeping: {section_name} ({section_size} chars)")
    
    # Rebuild trimmed MEMORY.md
    new_content_parts = []
    
    # Add header if it exists
    if "header" in kept_sections:
        new_content_parts.append(kept_sections["header"])
        del kept_sections["header"]
    
    # Add kept sections
    for section_name, section_content in kept_sections.items():
        new_content_parts.append(section_content)
    
    # Add references to archived content
    if archived_refs:
        new_content_parts.append("\n## Archived Sections")
        new_content_parts.append("\n*Content moved to vault for space:*\n")
        for ref in archived_refs:
            new_content_parts.append(ref)
        new_content_parts.append(f"\n*Full archive index: [[Archives/MEMORY-INDEX.md|Memory Archive Index]]*")
    
    new_content = '\n'.join(new_content_parts)
    new_size = len(new_content)
    
    # Write trimmed version
    with open(MEMORY_FILE, 'w') as f:
        f.write(new_content)
    
    print(f"✂️  TRIMMED: {original_size:,} → {new_size:,} chars ({original_size-new_size:,} saved)")
    print(f"📚 Archived {len(archived_refs)} sections to vault")
    print(f"📖 Archive index: {MEMORY_INDEX}")
    
    return True

def main():
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        print("🔧 Force trimming MEMORY.md...")
        return 0 if auto_trim_memory() else 1
    
    # Check if trimming is needed
    size = get_memory_size()
    
    if size > 4000:
        print(f"🚨 CRITICAL: MEMORY.md is {size:,} chars (>4,000) - auto-trimming...")
        return 0 if auto_trim_memory() else 1
    elif size > 3000:
        print(f"⚠️  WARNING: MEMORY.md is {size:,} chars (>3,000) - auto-trimming...")
        return 0 if auto_trim_memory() else 1
    else:
        print(f"✅ MEMORY.md size OK: {size:,} chars")
        return 0

if __name__ == "__main__":
    exit(main())
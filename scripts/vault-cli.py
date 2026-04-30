#!/usr/bin/env python3
"""
Simple Obsidian vault operations for kelly-vault
"""
import os
import re
import json
from datetime import datetime
from pathlib import Path

VAULT_PATH = "/data/kelly-vault"

def create_note(path, content="", template=None):
    """Create a new note with optional template"""
    full_path = Path(VAULT_PATH) / f"{path}.md"
    
    # Create parent directories if needed
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    if template == "daily":
        content = f"""# {datetime.now().strftime('%B %d, %Y')}

## Activity Log

{content}
"""
    
    with open(full_path, 'w') as f:
        f.write(content)
    
    print(f"Created: {full_path}")
    return str(full_path)

def search_notes(query):
    """Search note names for query"""
    matches = []
    vault = Path(VAULT_PATH)
    
    for md_file in vault.rglob("*.md"):
        if query.lower() in md_file.stem.lower():
            rel_path = md_file.relative_to(vault)
            matches.append(str(rel_path))
    
    return matches

def search_content(query):
    """Search inside note content"""
    matches = []
    vault = Path(VAULT_PATH)
    
    for md_file in vault.rglob("*.md"):
        try:
            with open(md_file, 'r') as f:
                content = f.read()
                if query.lower() in content.lower():
                    rel_path = md_file.relative_to(vault)
                    # Find the line with the match
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if query.lower() in line.lower():
                            matches.append({
                                'file': str(rel_path),
                                'line': i + 1,
                                'content': line.strip()
                            })
                            break
        except:
            continue
    
    return matches

def update_links(old_path, new_path):
    """Update [[wikilinks]] when moving files"""
    vault = Path(VAULT_PATH)
    old_name = Path(old_path).stem
    new_name = Path(new_path).stem
    
    if old_name == new_name:
        return
    
    updated_files = []
    
    for md_file in vault.rglob("*.md"):
        try:
            with open(md_file, 'r') as f:
                content = f.read()
            
            # Update [[old_name]] to [[new_name]]
            old_link_pattern = rf'\[\[{re.escape(old_name)}\]\]'
            new_content = re.sub(old_link_pattern, f'[[{new_name}]]', content)
            
            if content != new_content:
                with open(md_file, 'w') as f:
                    f.write(new_content)
                updated_files.append(str(md_file.relative_to(vault)))
        except:
            continue
    
    return updated_files

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Kelly Vault CLI")
    parser.add_argument("command", choices=["create", "search", "search-content", "daily"])
    parser.add_argument("--path", help="Note path (without .md)")
    parser.add_argument("--content", default="", help="Note content")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--template", help="Template to use")
    
    args = parser.parse_args()
    
    if args.command == "create":
        if not args.path:
            print("Error: --path required")
            return
        create_note(args.path, args.content, args.template)
    
    elif args.command == "daily":
        date_str = datetime.now().strftime('%Y-%m-%d')
        path = f"01-Daily/2026/{date_str}"
        create_note(path, args.content, "daily")
    
    elif args.command == "search":
        if not args.query:
            print("Error: --query required")
            return
        results = search_notes(args.query)
        for result in results:
            print(result)
    
    elif args.command == "search-content":
        if not args.query:
            print("Error: --query required")
            return
        results = search_content(args.query)
        for result in results:
            print(f"{result['file']}:{result['line']} - {result['content']}")

if __name__ == "__main__":
    main()
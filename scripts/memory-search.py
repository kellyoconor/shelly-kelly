#!/usr/bin/env python3
"""
Search across all memory files (current + archived)
So nothing ever gets forgotten
"""
import os
import glob
import re

MEMORY_FILE = "/data/workspace/MEMORY.md"
VAULT_ARCHIVE = "/data/kelly-vault/Archives/memory"
DAILY_MEMORY = "/data/workspace/memory"

def search_all_memory(query, limit=10):
    """Search across current memory, archived sections, and daily files"""
    results = []
    
    # Search current MEMORY.md
    if os.path.exists(MEMORY_FILE):
        results.extend(search_file(MEMORY_FILE, query, "Current Memory"))
    
    # Search archived sections
    if os.path.exists(VAULT_ARCHIVE):
        for archive_file in glob.glob(os.path.join(VAULT_ARCHIVE, "*.md")):
            filename = os.path.basename(archive_file)
            results.extend(search_file(archive_file, query, f"Archive: {filename}"))
    
    # Search daily memory files
    if os.path.exists(DAILY_MEMORY):
        for daily_file in glob.glob(os.path.join(DAILY_MEMORY, "*.md")):
            filename = os.path.basename(daily_file)
            results.extend(search_file(daily_file, query, f"Daily: {filename}"))
    
    # Sort by relevance (simple: more matches = higher score)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results[:limit]

def search_file(filepath, query, source):
    """Search a single file for the query"""
    results = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
    except Exception as e:
        return results
    
    lines = content.split('\n')
    query_lower = query.lower()
    
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            # Calculate simple relevance score
            score = line.lower().count(query_lower)
            
            # Get context (line before and after)
            start = max(0, i-1)
            end = min(len(lines), i+2)
            context = '\n'.join(lines[start:end])
            
            results.append({
                'score': score,
                'source': source,
                'line_num': i+1,
                'line': line.strip(),
                'context': context,
                'file': filepath
            })
    
    return results

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 memory-search.py <query> [limit]")
        print("Example: python3 memory-search.py 'session cleanup'")
        return 1
    
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"🔍 Searching all memory for: '{query}'")
    print("="*50)
    
    results = search_all_memory(query, limit)
    
    if not results:
        print("❌ No matches found")
        return 1
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['source']} (line {result['line_num']}) - Score: {result['score']}")
        print(f"   📍 {result['line']}")
        
        # Show context if different from main line
        if '\n' in result['context'] and result['context'] != result['line']:
            print(f"   📄 Context:")
            for ctx_line in result['context'].split('\n'):
                if ctx_line.strip():
                    marker = "   ➤ " if query.lower() in ctx_line.lower() else "     "
                    print(f"{marker}{ctx_line.strip()}")
    
    print(f"\n✅ Found {len(results)} matches")
    
    return 0

if __name__ == "__main__":
    exit(main())
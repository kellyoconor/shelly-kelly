#!/usr/bin/env python3
"""
Vault file writer with automatic sync to Kelly's Obsidian.
Creates/writes files and immediately pushes to ensure visibility.
"""

import os
import sys
import subprocess

def write_and_push(file_path, content):
    """Write content to vault file and auto-push to sync with Obsidian."""
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the file
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully wrote {len(content)} bytes to {file_path}")
    
    # Auto-push to ensure Kelly sees the changes
    try:
        subprocess.run(["/data/workspace/scripts/auto-push-vault.sh"], check=True, capture_output=True)
        print("Auto-pushed to vault for immediate sync")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Auto-push failed ({e}), but file was saved locally")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 vault-write.py 'file_path' 'content'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    content = sys.argv[2]
    
    write_and_push(file_path, content)
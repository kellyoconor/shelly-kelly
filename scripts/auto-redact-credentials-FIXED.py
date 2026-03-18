#!/usr/bin/env python3
"""
Auto-redact exposed API credentials in files that might be committed or logged
FIXED: No longer redacts environment variables (services need those to function)
Instead focuses on preventing credentials from appearing in git-tracked files, logs, and memory
"""

import json
import os
import re
import shutil
import glob
from datetime import datetime

CONFIG_PATH = "/data/.clawdbot/openclaw.json"

# Credential patterns to detect and redact from file content
CREDENTIAL_PATTERNS = [
    (r'sk-[a-zA-Z0-9_-]{20,}', 'OPENAI_API_KEY'),
    (r'[0-9]{5,8}', 'CLIENT_ID'),  # Strava/Spotify client IDs
    (r'[a-f0-9]{32,}', 'CLIENT_SECRET'),  # Long hex secrets
    (r'ya29\.[a-zA-Z0-9_-]{50,}', 'GOOGLE_TOKEN'),  # Google OAuth tokens
    (r'[a-zA-Z0-9_-]{40,}', 'GENERIC_SECRET')  # Generic long secrets
]

# File paths to scan for exposed credentials
SCAN_PATHS = [
    "/data/workspace/memory/*.md",
    "/data/workspace/*.md", 
    "/data/workspace/scripts/*.py",
    "/data/workspace/.git/logs/HEAD",
    "/tmp/*.log",
    "/data/.clawdbot/logs/*.log"
]

# Files that should never contain credentials
NEVER_CREDENTIAL_FILES = [
    "MEMORY.md",
    "AGENTS.md", 
    "memory/2026-*.md"
]

def get_env_credentials():
    """Get actual credential values from environment for detection"""
    credentials = {}
    
    # Get values from current environment
    for key in ["OPENAI_API_KEY", "STRAVA_CLIENT_SECRET", "BRAVE_API_KEY", 
                "GOOGLE_CLIENT_SECRET", "KALSHI_API_KEY", "ELEVENLABS_API_KEY", "SPOTIFY_CLIENT_SECRET"]:
        value = os.environ.get(key)
        if value and value not in ["REDACTED_IN_ENV_FILE", "__OPENCLAW_REDACTED__", ""]:
            credentials[key] = value
            
    return credentials

def redact_file_content(file_path, credentials):
    """Scan and redact credentials from a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        redacted_count = 0
        
        # Check for actual credential values
        for cred_name, cred_value in credentials.items():
            if cred_value in content:
                content = content.replace(cred_value, f"[REDACTED_{cred_name}]")
                redacted_count += 1
        
        # Check for credential patterns
        for pattern, cred_type in CREDENTIAL_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, f"[REDACTED_{cred_type}]", content)
                redacted_count += len(matches)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return redacted_count
            
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")
        
    return 0

def main():
    print("🔍 Scanning for exposed credentials in files...")
    
    # Get environment credentials for detection
    credentials = get_env_credentials()
    
    total_redactions = 0
    scanned_files = 0
    
    # Scan specified paths
    for path_pattern in SCAN_PATHS:
        for file_path in glob.glob(path_pattern):
            if os.path.isfile(file_path):
                scanned_files += 1
                redacted = redact_file_content(file_path, credentials)
                if redacted > 0:
                    total_redactions += redacted
                    print(f"🔒 Redacted {redacted} credentials from: {file_path}")
    
    if total_redactions > 0:
        print(f"🔒 SECURITY FIX: Redacted {total_redactions} exposed credentials across {scanned_files} files")
        
        # Log the security fix
        log_entry = f"\\n{datetime.now().isoformat()}: Auto-redacted {total_redactions} exposed credentials from files\\n"
        with open("/data/workspace/memory/security-log.md", "a") as f:
            f.write(log_entry)
    else:
        print(f"✅ No exposed credentials found - scanned {scanned_files} files, all clean")

if __name__ == "__main__":
    main()
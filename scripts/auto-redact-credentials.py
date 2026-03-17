#!/usr/bin/env python3
"""
Auto-redact exposed API credentials in openclaw.json
Runs on startup to prevent Railway deployment credential exposure
"""

import json
import os
import shutil
from datetime import datetime

CONFIG_PATH = "/data/.clawdbot/openclaw.json"

# Credentials that should be redacted (never stored in plain text)
REDACT_KEYS = [
    "OPENAI_API_KEY",
    "STRAVA_CLIENT_SECRET", 
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REFRESH_TOKEN",
    "KALSHI_API_KEY",
    "ELEVENLABS_API_KEY",
    "BRAVE_API_KEY",
    "SPOTIFY_CLIENT_SECRET"
]

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Config not found: {CONFIG_PATH}")
        return
    
    # Backup original
    backup_path = f"{CONFIG_PATH}.backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    shutil.copy2(CONFIG_PATH, backup_path)
    
    # Load and check config
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    changed = False
    exposed_keys = []
    
    # Check env.vars section
    if "env" in config and "vars" in config["env"]:
        for key in REDACT_KEYS:
            if key in config["env"]["vars"]:
                value = config["env"]["vars"][key]
                # If it's not already redacted and looks like a real credential
                if value not in ["REDACTED_IN_ENV_FILE", "__OPENCLAW_REDACTED__"] and len(str(value)) > 10:
                    exposed_keys.append(key)
                    config["env"]["vars"][key] = "REDACTED_IN_ENV_FILE"
                    changed = True
    
    if changed:
        # Write redacted config
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"🔒 AUTO-REDACTED {len(exposed_keys)} exposed credentials:")
        for key in exposed_keys:
            print(f"  - {key}")
        print(f"Backup saved: {backup_path}")
    else:
        # Remove unnecessary backup
        os.remove(backup_path)
        print("✅ No exposed credentials found - config already secure")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Auto-commit utility for vault changes.
Call this after any script modifies vault files to prevent merge conflicts.
"""

import subprocess
import os

def auto_commit_vault(quiet=True):
    """Auto-commit any changes in the kelly-vault"""
    try:
        # Change to vault directory
        vault_dir = "/data/kelly-vault"
        
        # Check if there are changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=vault_dir,
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():  # There are changes
            # Add all changes
            subprocess.run(["git", "add", "-A"], cwd=vault_dir, check=True)
            
            # Commit with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"Auto-commit: {timestamp}"
            
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=vault_dir,
                check=True,
                capture_output=quiet
            )
            
            if not quiet:
                print(f"✅ Auto-committed vault changes: {timestamp}")
            return True
        else:
            if not quiet:
                print("ℹ️ No vault changes to commit")
            return False
            
    except subprocess.CalledProcessError as e:
        if not quiet:
            print(f"❌ Auto-commit failed: {e}")
        return False
    except Exception as e:
        if not quiet:
            print(f"❌ Auto-commit error: {e}")
        return False

if __name__ == "__main__":
    import sys
    quiet = "--quiet" in sys.argv
    auto_commit_vault(quiet=quiet)
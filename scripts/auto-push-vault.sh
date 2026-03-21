#!/bin/bash
# Auto-commit and push vault changes immediately after file creation/modification

cd /data/kelly-vault

# Check if there are any changes
if [ -n "$(git status --porcelain)" ]; then
    echo "Auto-pushing vault changes..."
    
    # Add all changes
    git add -A
    
    # Commit with timestamp
    git commit -m "Auto-push: $(date '+%Y-%m-%d %H:%M:%S')"
    
    # Pull with rebase to handle conflicts
    git pull --rebase origin main
    
    # Push to remote
    git push origin main
    
    echo "Vault changes pushed successfully"
else
    echo "No vault changes to push"
fi
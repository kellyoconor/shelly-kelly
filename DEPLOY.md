# Deployment Guide - OpenClaw Workspace

## 🚨 Critical: Post-Deploy Dependencies

**Problem:** Railway redeploys wipe pip packages from the Docker environment.

**Solution:** Run dependency restoration after each deploy.

## 📦 Required Dependencies

The workspace requires these Python packages to function:

- `agentmail` - Email handling (AgentMail skill)  
- `watchdog` - File monitoring (Research Co-Pilot)
- `pydantic` - Data validation
- `websockets` - Real-time connections
- `requests` - HTTP requests
- `aiofiles` - Async file operations

## 🔧 Post-Deploy Restoration

**After each Railway redeploy, run:**

```bash
# Quick fix - restore dependencies
bash /data/workspace/scripts/install-dependencies.sh

# Full reset - restore everything  
bash /data/workspace/scripts/post-deploy-setup.sh
```

## 🤖 Automated Process

**For manual deploys:**
1. `git push origin main` (triggers Railway redeploy)
2. Wait for redeploy to complete (WhatsApp reconnect)
3. Run: `exec: bash /data/workspace/scripts/post-deploy-setup.sh`

## 📋 Service Status After Deploy

Check these services are working:

- ✅ **AgentMail:** `cd skills/agentmail && python3 scripts/client.py status`
- ✅ **Research Co-Pilot:** `cd kelly-research-copilot && python3 src/main.py --status`  
- ✅ **Enhanced Welly:** `cd welly && ./status-enhanced-welly.sh`
- ✅ **Kelly State Pipeline:** Automatic (built into message tools)

## 🚀 Future: Docker Solution

**Ideal fix:** Add requirements.txt to OpenClaw's Docker image so packages persist.

**Current workaround:** Post-deploy restoration scripts.
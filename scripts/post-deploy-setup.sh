#!/bin/bash

# Post-Deploy Setup Script
# Automatically restore workspace after Railway redeployments

echo "🚀 Post-Deploy Setup Starting..."
echo "================================"

# 1. Install Python dependencies
echo "📦 Step 1: Installing Python dependencies..."
bash /data/workspace/scripts/install-dependencies.sh

# 2. Restart monitoring services  
echo ""
echo "💙 Step 2: Starting monitoring services..."
cd /data/workspace/welly
./start-enhanced-welly.sh > /dev/null 2>&1

# 3. Check service status
echo ""
echo "🩺 Step 3: Verifying service status..."

# Check AgentMail
cd /data/workspace/skills/agentmail
if python3 scripts/client.py status > /dev/null 2>&1; then
    echo "✅ AgentMail: Running"
else
    echo "❌ AgentMail: Failed"
fi

# Check Research Co-Pilot
cd /data/workspace/kelly-research-copilot
if python3 src/main.py --status > /dev/null 2>&1; then
    echo "✅ Research Co-Pilot: Running"
else
    echo "❌ Research Co-Pilot: Failed"
fi

# Check Welly
cd /data/workspace/welly
if ./status-enhanced-welly.sh | grep -q "Running"; then
    echo "✅ Enhanced Welly: Running"
else
    echo "❌ Enhanced Welly: Failed"
fi

echo ""
echo "🎯 Post-Deploy Setup Complete"
echo "All workspace services should now be operational"

cd /data/workspace
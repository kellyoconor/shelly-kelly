#!/bin/bash

# Install Python dependencies for OpenClaw workspace
# Run this after Railway deployments to restore missing packages

echo "🔧 Installing OpenClaw workspace dependencies..."

# Install from requirements.txt
if [[ -f "/data/workspace/requirements.txt" ]]; then
    echo "📦 Installing from requirements.txt..."
    pip install -r /data/workspace/requirements.txt --break-system-packages
    
    if [[ $? -eq 0 ]]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Some dependencies failed to install"
    fi
else
    echo "❌ requirements.txt not found"
fi

# Test key components
echo ""
echo "🧪 Testing installed packages..."

# Test AgentMail
python3 -c "import agentmail; print('✅ AgentMail: OK')" 2>/dev/null || echo "❌ AgentMail: Failed"

# Test Watchdog
python3 -c "import watchdog; print('✅ Watchdog: OK')" 2>/dev/null || echo "❌ Watchdog: Failed"

# Test Research Co-Pilot
cd /data/workspace/kelly-research-copilot
python3 src/main.py --status > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
    echo "✅ Research Co-Pilot: OK"
else
    echo "❌ Research Co-Pilot: Failed"
fi
cd /data/workspace

echo ""
echo "🎯 Dependency installation complete"
echo "Run this script after Railway redeploys to restore packages"
#!/bin/bash
# Start Welly Always-On Service (Proper daemon process)

set -e

WELLY_DIR="/data/workspace/welly"

cd "$WELLY_DIR"

# Stop any existing service first
python3 welly-daemon.py stop 2>/dev/null || true

# Start the proper daemon service
echo "🚀 Starting Welly Always-On service..."
python3 welly-daemon.py start

# Give it a moment to start
sleep 2

# Check status
if python3 welly-daemon.py status >/dev/null 2>&1; then
    echo "✅ Welly Always-On service started successfully"
    echo "   Status: python3 $WELLY_DIR/welly-daemon.py status"
    echo "   Logs: tail -f /data/workspace/memory/welly-daemon.log"
else
    echo "❌ Failed to start Welly Always-On service"
    echo "📝 Check logs: tail /data/workspace/memory/welly-daemon.log"
    exit 1
fi
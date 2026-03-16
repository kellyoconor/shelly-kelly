#!/bin/bash
# Start Welly Always-On Service (File-based for Docker/container environment)

set -e

WELLY_DIR="/data/workspace/welly"
PID_FILE="$WELLY_DIR/welly-monitor.pid"
LOG_FILE="/data/workspace/memory/welly-monitor.log"

cd "$WELLY_DIR"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "💙 Welly Always-On service is already running (PID: $PID)"
        exit 0
    else
        echo "🧹 Cleaning up stale PID file..."
        rm -f "$PID_FILE"
    fi
fi

# Start the service in background
echo "🚀 Starting Welly Always-On service..."
echo "📝 Logs: $LOG_FILE"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Start the monitor in background
nohup python3 welly-monitor.py start >> "$LOG_FILE" 2>&1 &
MONITOR_PID=$!

# Save PID
echo "$MONITOR_PID" > "$PID_FILE"

# Give it a moment to start
sleep 2

# Check if it started successfully
if ps -p $MONITOR_PID > /dev/null 2>&1; then
    echo "✅ Welly Always-On service started successfully"
    echo "   PID: $MONITOR_PID"
    echo "   Status: python3 $WELLY_DIR/welly-monitor.py status"
    echo "   Logs: tail -f $LOG_FILE"
else
    echo "❌ Failed to start Welly Always-On service"
    echo "📝 Check logs: tail $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi
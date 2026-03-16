#!/bin/bash
# Stop Welly Always-On Service (File-based for Docker/container environment)

set -e

WELLY_DIR="/data/workspace/welly"
PID_FILE="$WELLY_DIR/welly-monitor.pid"

cd "$WELLY_DIR"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "💙 Welly Always-On service is not running (no PID file)"
    exit 0
fi

# Get PID and check if process is running
PID=$(cat "$PID_FILE")

if ! ps -p $PID > /dev/null 2>&1; then
    echo "💙 Welly Always-On service is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 Stopping Welly Always-On service (PID: $PID)..."

# Send SIGTERM first
kill -TERM $PID 2>/dev/null || true

# Wait for graceful shutdown
TIMEOUT=10
COUNTER=0
while ps -p $PID > /dev/null 2>&1; do
    if [ $COUNTER -ge $TIMEOUT ]; then
        echo "⚠️  Graceful shutdown timed out, forcing termination..."
        kill -KILL $PID 2>/dev/null || true
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
done

# Clean up PID file
rm -f "$PID_FILE"

echo "✅ Welly Always-On service stopped"
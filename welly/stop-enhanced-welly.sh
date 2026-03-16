#!/bin/bash

# Enhanced Welly Stop Script

MEMORY_DIR="/data/workspace/memory"

echo "🛑 Stopping Enhanced Welly System..."

# Stop health monitor first
HEALTH_PID_FILE="$MEMORY_DIR/welly-health.pid"
if [[ -f "$HEALTH_PID_FILE" ]]; then
    HEALTH_PID=$(cat "$HEALTH_PID_FILE")
    if kill -0 "$HEALTH_PID" 2>/dev/null; then
        echo "   Stopping Health Monitor (PID $HEALTH_PID)..."
        kill "$HEALTH_PID"
        sleep 2
        # Force kill if still running
        if kill -0 "$HEALTH_PID" 2>/dev/null; then
            echo "   Force stopping Health Monitor..."
            kill -9 "$HEALTH_PID"
        fi
    fi
    rm -f "$HEALTH_PID_FILE"
fi

# Stop enhanced monitor
MONITOR_PID_FILE="$MEMORY_DIR/welly-enhanced.pid"
if [[ -f "$MONITOR_PID_FILE" ]]; then
    MONITOR_PID=$(cat "$MONITOR_PID_FILE")
    if kill -0 "$MONITOR_PID" 2>/dev/null; then
        echo "   Stopping Enhanced Monitor (PID $MONITOR_PID)..."
        kill "$MONITOR_PID"
        sleep 2
        # Force kill if still running
        if kill -0 "$MONITOR_PID" 2>/dev/null; then
            echo "   Force stopping Enhanced Monitor..."
            kill -9 "$MONITOR_PID"
        fi
    fi
    rm -f "$MONITOR_PID_FILE"
fi

# Clean up any other welly processes
echo "   Cleaning up any remaining Welly processes..."
pkill -f welly-monitor-enhanced.py || true
pkill -f welly-health-monitor.py || true
pkill -f welly-monitor.py || true

sleep 1

echo "✅ Enhanced Welly System stopped"
echo ""
echo "📊 Final Status:"
if pgrep -f "welly.*monitor" > /dev/null; then
    echo "   ⚠️  Some Welly processes may still be running:"
    pgrep -f "welly.*monitor" | while read pid; do
        echo "     PID $pid: $(ps -p $pid -o comm=)"
    done
else
    echo "   ✅ All Welly processes stopped"
fi
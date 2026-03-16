#!/bin/bash

# Enhanced Welly Status Script

WELLY_DIR="/data/workspace/welly"
MEMORY_DIR="/data/workspace/memory"

echo "💙 Enhanced Welly System Status"
echo "=============================="

# Check PIDs
MONITOR_PID_FILE="$MEMORY_DIR/welly-enhanced.pid"
HEALTH_PID_FILE="$MEMORY_DIR/welly-health.pid"

if [[ -f "$MONITOR_PID_FILE" ]]; then
    MONITOR_PID=$(cat "$MONITOR_PID_FILE")
    if kill -0 "$MONITOR_PID" 2>/dev/null; then
        echo "✅ Enhanced Monitor: Running (PID $MONITOR_PID)"
    else
        echo "❌ Enhanced Monitor: Not running (stale PID)"
    fi
else
    echo "❌ Enhanced Monitor: No PID file found"
fi

if [[ -f "$HEALTH_PID_FILE" ]]; then
    HEALTH_PID=$(cat "$HEALTH_PID_FILE")
    if kill -0 "$HEALTH_PID" 2>/dev/null; then
        echo "✅ Health Monitor: Running (PID $HEALTH_PID)"
    else
        echo "❌ Health Monitor: Not running (stale PID)"
    fi
else
    echo "❌ Health Monitor: No PID file found"
fi

echo ""

# Check component status
cd "$WELLY_DIR"

echo "📊 Enhanced Monitor Status:"
python3 welly-monitor-enhanced.py status 2>/dev/null || echo "   ❌ Could not get enhanced monitor status"

echo ""

echo "🩺 Health Monitor Status:"
python3 welly-health-monitor.py status 2>/dev/null || echo "   ❌ Could not get health monitor status"

echo ""

# Show recent log entries
echo "📋 Recent Activity (last 5 lines):"
if [[ -f "$MEMORY_DIR/welly-enhanced.log" ]]; then
    echo "   Enhanced Monitor:"
    tail -5 "$MEMORY_DIR/welly-enhanced.log" | sed 's/^/     /'
else
    echo "   ❌ No enhanced monitor log found"
fi

if [[ -f "$MEMORY_DIR/welly-health.log" ]]; then
    echo "   Health Monitor:"
    tail -5 "$MEMORY_DIR/welly-health.log" | sed 's/^/     /'
else
    echo "   ❌ No health monitor log found"
fi

echo ""
echo "🔧 Management Commands:"
echo "   Start: ./start-enhanced-welly.sh"
echo "   Stop:  ./stop-enhanced-welly.sh"
echo "   Logs:  tail -f $MEMORY_DIR/welly-enhanced.log"
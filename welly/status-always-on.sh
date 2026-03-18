#!/bin/bash
# Check Welly Always-On Service Status (File-based for Docker/container environment)

WELLY_DIR="/data/workspace/welly"
PID_FILE="$WELLY_DIR/welly-daemon.pid"
LOG_FILE="/data/workspace/memory/welly-daemon.log"

cd "$WELLY_DIR"

echo "💙 Welly Always-On Service Status"
echo "=================================="

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "   Status: ❌ Not running"
    echo "   Reason: No PID file found"
else
    PID=$(cat "$PID_FILE")
    
    # Check if process is actually running
    if ps -p $PID > /dev/null 2>&1; then
        echo "   Status: ✅ Running"
        echo "   PID: $PID"
        echo "   Started: $(ps -o lstart= -p $PID 2>/dev/null | tr -s ' ')"
        echo "   Uptime: $(ps -o etime= -p $PID 2>/dev/null | tr -d ' ')"
    else
        echo "   Status: ❌ Not running"
        echo "   Reason: Process $PID not found (stale PID file)"
    fi
fi

# Show log file info
echo ""
echo "📝 Log Information"
echo "=================="
if [ -f "$LOG_FILE" ]; then
    echo "   Log file: $LOG_FILE"
    echo "   Size: $(du -h "$LOG_FILE" | cut -f1)"
    echo "   Modified: $(stat -c %y "$LOG_FILE" | cut -d'.' -f1)"
    echo ""
    echo "📖 Recent Log Entries (last 5 lines):"
    echo "   $(tail -5 "$LOG_FILE" | sed 's/^/   /')"
else
    echo "   Log file: ❌ Not found"
fi

# Show component status if monitor is available
echo ""
echo "🔧 Component Status"
echo "==================="
if python3 -c "import sys; sys.path.append('$WELLY_DIR'); from welly_monitor import WellyMonitor" 2>/dev/null; then
    python3 welly-monitor.py status 2>/dev/null || echo "   Monitor: ❌ Status check failed"
else
    echo "   Monitor: ❌ Component not available"
fi

# Show recent activity
echo ""
echo "📊 Recent Activity"
echo "=================="
MEMORY_DIR="/data/workspace/memory"
if [ -d "$MEMORY_DIR" ]; then
    echo "   Recent files in memory:"
    ls -lt "$MEMORY_DIR"/welly* 2>/dev/null | head -3 | sed 's/^/   /' || echo "   No recent Welly files"
else
    echo "   Memory directory: ❌ Not found"
fi

echo ""
echo "🔄 Quick Commands"
echo "================="
echo "   Start:  $WELLY_DIR/start-always-on.sh"
echo "   Stop:   $WELLY_DIR/stop-always-on.sh" 
echo "   Logs:   tail -f $LOG_FILE"
echo "   Test:   python3 $WELLY_DIR/test-always-on.py"
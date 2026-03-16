#!/bin/bash

# Enhanced Welly Startup Script
# Starts both the enhanced monitor and health watchdog

WELLY_DIR="/data/workspace/welly"
MEMORY_DIR="/data/workspace/memory"

# Ensure memory directory exists
mkdir -p "$MEMORY_DIR"

echo "🔧 Starting Enhanced Welly System..."

# Stop any existing Welly processes
echo "   Stopping existing Welly processes..."
pkill -f welly-monitor.py || true
pkill -f welly-health-monitor.py || true
sleep 2

# Start enhanced monitor in background
echo "   Starting Enhanced Welly Monitor..."
cd "$WELLY_DIR"
nohup python3 welly-monitor-enhanced.py start > "$MEMORY_DIR/welly-enhanced.log" 2>&1 &
MONITOR_PID=$!

# Give monitor time to start
sleep 3

# Start health monitor in background
echo "   Starting Welly Health Monitor..."
nohup python3 welly-health-monitor.py start > "$MEMORY_DIR/welly-health.log" 2>&1 &
HEALTH_PID=$!

# Save PIDs
echo "$MONITOR_PID" > "$MEMORY_DIR/welly-enhanced.pid"
echo "$HEALTH_PID" > "$MEMORY_DIR/welly-health.pid"

echo "✅ Enhanced Welly System Started"
echo "   Monitor PID: $MONITOR_PID"
echo "   Health Monitor PID: $HEALTH_PID"
echo "   Logs:"
echo "     Monitor: $MEMORY_DIR/welly-enhanced.log"
echo "     Health: $MEMORY_DIR/welly-health.log"
echo ""
echo "🩺 System Features:"
echo "   ✅ Self-healing error recovery"
echo "   🔄 Auto-restart stuck components"
echo "   ⏰ Adaptive cycle timing (10-30 min)"
echo "   🚨 Health checks every 5 minutes"
echo "   📊 Comprehensive failure tracking"
echo ""
echo "Use 'tail -f $MEMORY_DIR/welly-enhanced.log' to monitor"
echo "Use './status-enhanced-welly.sh' to check status"
# Heartbeat Tasks - Always-On Welly Integration

## Always-On Welly Status Check

```python
import sys
import subprocess
from pathlib import Path

# Check if Always-On Welly is running
try:
    welly_dir = Path("/data/workspace/welly")
    
    # Check service status
    result = subprocess.run([
        str(welly_dir / "status-always-on.sh")
    ], capture_output=True, text=True)
    
    if "✅ Running" in result.stdout:
        # Service is running - minimal heartbeat needed
        print("💙 Always-On Welly is monitoring in background")
        
        # Check if there are any fresh insights to share
        status_result = subprocess.run([
            "python3", str(welly_dir / "welly-monitor.py"), "status"
        ], capture_output=True, text=True, cwd=str(welly_dir))
        
        if "Last pattern analysis:" in status_result.stdout and "None" not in status_result.stdout:
            print("💙 Background pattern analysis is active")
    else:
        # Service not running - fallback to manual check
        print("💙 Always-On Welly not running - checking manually...")
        
        # Use existing Welly heartbeat
        sys.path.append('/data/workspace/welly')
        from heartbeat_integration import WellyHeartbeatIntegration
        
        integration = WellyHeartbeatIntegration()
        result = integration.run_integrated_heartbeat()
        
        for message in result.get("messages_sent", []):
            print(f"💙 {message['message']}")
            
except Exception as e:
    print(f"💙 Welly heartbeat check failed: {e}")
    # Silent fallback - don't break heartbeat system
    pass
```

Keep this minimal - Always-On Welly handles most monitoring automatically.
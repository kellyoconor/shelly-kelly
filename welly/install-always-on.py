#!/usr/bin/env python3
"""
Welly Always-On Installation Script

Installs and configures the always-on pattern detection service while
preserving the existing manual check-in system.

This script:
1. Sets up the new service components
2. Configures systemd service for persistence  
3. Tests integration with existing Welly
4. Provides management commands
"""

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

class WellyAlwaysOnInstaller:
    """Install and manage the always-on Welly service"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.welly_dir = self.workspace / "welly"
        self.service_file = self.welly_dir / "welly-monitor.service"
        self.systemd_service_path = "/etc/systemd/system/welly-monitor.service"
        
    def check_prerequisites(self) -> Dict:
        """Check that existing Welly system is ready"""
        check_result = {
            "existing_welly": False,
            "database_exists": False,
            "skills_available": False,
            "python_modules": False,
            "systemd_available": False,
            "errors": []
        }
        
        try:
            # Check existing Welly installation
            if (self.welly_dir / "welly.py").exists():
                check_result["existing_welly"] = True
            else:
                check_result["errors"].append("Existing Welly installation not found")
            
            # Check database
            if (self.welly_dir / "welly_memory.db").exists():
                check_result["database_exists"] = True
            else:
                check_result["errors"].append("Welly database not found - run 'python3 welly.py setup' first")
            
            # Check skills
            oura_skill = self.workspace / "skills" / "oura" / "scripts" / "oura.py"
            strava_skill = self.workspace / "skills" / "strava" / "scripts" / "strava.py"
            
            if oura_skill.exists() and strava_skill.exists():
                check_result["skills_available"] = True
            else:
                check_result["errors"].append("Oura/Strava skills not found")
            
            # Check Python modules
            try:
                import sqlite3
                import asyncio
                check_result["python_modules"] = True
            except ImportError as e:
                check_result["errors"].append(f"Missing Python module: {e}")
            
            # Check systemd
            if shutil.which("systemctl"):
                check_result["systemd_available"] = True
            else:
                check_result["errors"].append("Systemd not available")
        
        except Exception as e:
            check_result["errors"].append(f"Prerequisite check failed: {e}")
        
        return check_result
    
    def install_service(self) -> Dict:
        """Install the always-on service"""
        install_result = {
            "steps_completed": [],
            "errors": [],
            "service_installed": False
        }
        
        try:
            # Step 1: Check prerequisites
            prereqs = self.check_prerequisites()
            if prereqs["errors"]:
                install_result["errors"].extend(prereqs["errors"])
                return install_result
            
            install_result["steps_completed"].append("prerequisites_checked")
            
            # Step 2: Make new components executable
            for script in ["welly-monitor.py", "welly-poller.py", "welly-patterns.py", "welly-alerts.py"]:
                script_path = self.welly_dir / script
                if script_path.exists():
                    os.chmod(script_path, 0o755)
            
            install_result["steps_completed"].append("scripts_configured")
            
            # Step 3: Test new components
            test_result = self._test_components()
            if test_result["errors"]:
                install_result["errors"].extend(test_result["errors"])
                return install_result
            
            install_result["steps_completed"].append("components_tested")
            
            # Step 4: Install systemd service
            if self._install_systemd_service():
                install_result["steps_completed"].append("systemd_service_installed")
                install_result["service_installed"] = True
            else:
                install_result["errors"].append("Failed to install systemd service")
            
            # Step 5: Create management scripts
            self._create_management_scripts()
            install_result["steps_completed"].append("management_scripts_created")
            
        except Exception as e:
            install_result["errors"].append(f"Installation failed: {e}")
        
        return install_result
    
    def _test_components(self) -> Dict:
        """Test that new components work with existing Welly"""
        test_result = {
            "errors": [],
            "components_working": []
        }
        
        try:
            # Test poller
            poller_test = subprocess.run([
                "python3", str(self.welly_dir / "welly-poller.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            if poller_test.returncode == 0:
                test_result["components_working"].append("poller")
            else:
                test_result["errors"].append(f"Poller test failed: {poller_test.stderr}")
            
            # Test patterns
            patterns_test = subprocess.run([
                "python3", str(self.welly_dir / "welly-patterns.py"), "summary", "7"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            if patterns_test.returncode == 0:
                test_result["components_working"].append("patterns")
            else:
                test_result["errors"].append(f"Patterns test failed: {patterns_test.stderr}")
            
            # Test alerts
            alerts_test = subprocess.run([
                "python3", str(self.welly_dir / "welly-alerts.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            if alerts_test.returncode == 0:
                test_result["components_working"].append("alerts")
            else:
                test_result["errors"].append(f"Alerts test failed: {alerts_test.stderr}")
        
        except Exception as e:
            test_result["errors"].append(f"Component testing failed: {e}")
        
        return test_result
    
    def _install_systemd_service(self) -> bool:
        """Install systemd service for persistence"""
        try:
            # Copy service file to systemd location
            shutil.copy2(self.service_file, self.systemd_service_path)
            
            # Reload systemd
            subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            # Enable service (don't start yet)
            subprocess.run(["systemctl", "enable", "welly-monitor"], check=True)
            
            return True
            
        except Exception as e:
            print(f"Error installing systemd service: {e}")
            return False
    
    def _create_management_scripts(self):
        """Create convenience scripts for managing the service"""
        
        # Create start script
        start_script = self.welly_dir / "start-always-on.sh"
        with open(start_script, 'w') as f:
            f.write("""#!/bin/bash
# Start Welly always-on service

echo "🚀 Starting Welly Always-On Pattern Detection..."

# Check if already running
if systemctl is-active --quiet welly-monitor; then
    echo "   Service already running"
    systemctl status welly-monitor
else
    # Start the service
    systemctl start welly-monitor
    sleep 2
    
    if systemctl is-active --quiet welly-monitor; then
        echo "✅ Welly Monitor started successfully"
        echo "   Status: $(systemctl is-active welly-monitor)"
        echo "   Logs: journalctl -fu welly-monitor"
    else
        echo "❌ Failed to start Welly Monitor"
        systemctl status welly-monitor
        exit 1
    fi
fi
""")
        os.chmod(start_script, 0o755)
        
        # Create stop script
        stop_script = self.welly_dir / "stop-always-on.sh"
        with open(stop_script, 'w') as f:
            f.write("""#!/bin/bash
# Stop Welly always-on service

echo "🛑 Stopping Welly Always-On Pattern Detection..."

if systemctl is-active --quiet welly-monitor; then
    systemctl stop welly-monitor
    echo "✅ Welly Monitor stopped"
else
    echo "   Service was not running"
fi
""")
        os.chmod(stop_script, 0o755)
        
        # Create status script  
        status_script = self.welly_dir / "status-always-on.sh"
        with open(status_script, 'w') as f:
            f.write("""#!/bin/bash
# Check Welly always-on service status

echo "💙 Welly Always-On Service Status"
echo

# Systemd service status
echo "📋 Service Status:"
systemctl status welly-monitor --no-pager -l

echo
echo "📊 Component Status:"

# Monitor status
echo "   Monitor:"
python3 /data/workspace/welly/welly-monitor.py status 2>/dev/null | grep -E "Running:|Monitoring since:|Last alert:" || echo "     Not available"

# Poller status  
echo "   Data Poller:"
python3 /data/workspace/welly/welly-poller.py status 2>/dev/null | grep -E "Polling since:|Last.*poll:" || echo "     Not available"

# Alerts status
echo "   Alert System:"
python3 /data/workspace/welly/welly-alerts.py status 2>/dev/null | grep -E "Can send alert:|Alerts today:" || echo "     Not available"

echo
echo "📝 Recent Logs:"
journalctl -n 10 --no-pager -u welly-monitor | grep -v "^--"
""")
        os.chmod(status_script, 0o755)
    
    def start_service(self) -> bool:
        """Start the always-on service"""
        try:
            subprocess.run(["systemctl", "start", "welly-monitor"], check=True)
            return True
        except Exception as e:
            print(f"Error starting service: {e}")
            return False
    
    def stop_service(self) -> bool:
        """Stop the always-on service"""
        try:
            subprocess.run(["systemctl", "stop", "welly-monitor"], check=True)
            return True
        except Exception as e:
            print(f"Error stopping service: {e}")
            return False
    
    def get_service_status(self) -> Dict:
        """Get comprehensive service status"""
        status = {
            "systemd_status": "unknown",
            "service_running": False,
            "uptime": None,
            "errors": []
        }
        
        try:
            # Check systemd status
            result = subprocess.run([
                "systemctl", "is-active", "welly-monitor"
            ], capture_output=True, text=True)
            
            status["systemd_status"] = result.stdout.strip()
            status["service_running"] = status["systemd_status"] == "active"
            
            # Get uptime if running
            if status["service_running"]:
                uptime_result = subprocess.run([
                    "systemctl", "show", "welly-monitor", "--property=ActiveEnterTimestamp"
                ], capture_output=True, text=True)
                
                if uptime_result.returncode == 0:
                    timestamp_line = uptime_result.stdout.strip()
                    if "=" in timestamp_line:
                        timestamp_str = timestamp_line.split("=", 1)[1]
                        try:
                            start_time = datetime.strptime(timestamp_str, "%a %Y-%m-%d %H:%M:%S %Z")
                            uptime_delta = datetime.now() - start_time
                            status["uptime"] = str(uptime_delta).split(".")[0]  # Remove microseconds
                        except:
                            pass
        
        except Exception as e:
            status["errors"].append(f"Status check failed: {e}")
        
        return status
    
    def uninstall_service(self) -> Dict:
        """Uninstall the always-on service (preserves existing Welly)"""
        uninstall_result = {
            "steps_completed": [],
            "errors": []
        }
        
        try:
            # Stop service if running
            self.stop_service()
            uninstall_result["steps_completed"].append("service_stopped")
            
            # Disable service
            subprocess.run(["systemctl", "disable", "welly-monitor"], check=False)
            uninstall_result["steps_completed"].append("service_disabled")
            
            # Remove systemd service file
            if os.path.exists(self.systemd_service_path):
                os.remove(self.systemd_service_path)
                subprocess.run(["systemctl", "daemon-reload"], check=True)
            
            uninstall_result["steps_completed"].append("systemd_service_removed")
            
            # Remove always-on components (keep existing Welly)
            for component in ["welly-monitor.py", "welly-poller.py", "welly-patterns.py", "welly-alerts.py"]:
                component_path = self.welly_dir / component
                if component_path.exists():
                    os.remove(component_path)
            
            uninstall_result["steps_completed"].append("always_on_components_removed")
            
        except Exception as e:
            uninstall_result["errors"].append(f"Uninstall failed: {e}")
        
        return uninstall_result


def main():
    if len(sys.argv) < 2:
        print("Welly Always-On Installation & Management")
        print()
        print("Usage:")
        print("  python3 install-always-on.py install      # Install always-on service")
        print("  python3 install-always-on.py start        # Start the service")
        print("  python3 install-always-on.py stop         # Stop the service")
        print("  python3 install-always-on.py status       # Check service status")
        print("  python3 install-always-on.py check        # Check prerequisites")
        print("  python3 install-always-on.py uninstall    # Remove always-on service")
        print()
        print("Enhances existing Welly with always-on pattern detection")
        return
    
    installer = WellyAlwaysOnInstaller()
    command = sys.argv[1]
    
    if command == "install":
        print("🚀 Installing Welly Always-On Pattern Detection Service...")
        print("   This enhances your existing Welly without replacing it")
        print()
        
        result = installer.install_service()
        
        print("Installation Results:")
        for step in result["steps_completed"]:
            print(f"   ✅ {step.replace('_', ' ').title()}")
        
        for error in result["errors"]:
            print(f"   ❌ {error}")
        
        if result["service_installed"]:
            print()
            print("✅ Always-on service installed successfully!")
            print("   Start with: python3 install-always-on.py start")
            print("   Status: python3 install-always-on.py status")
            print("   Or use: ./start-always-on.sh")
        else:
            print()
            print("❌ Installation incomplete. Check errors above.")
    
    elif command == "start":
        print("🚀 Starting Welly Always-On Service...")
        if installer.start_service():
            print("✅ Service started successfully")
            print("   Monitor with: journalctl -fu welly-monitor")
        else:
            print("❌ Failed to start service")
    
    elif command == "stop":
        print("🛑 Stopping Welly Always-On Service...")
        if installer.stop_service():
            print("✅ Service stopped")
        else:
            print("❌ Failed to stop service")
    
    elif command == "status":
        status = installer.get_service_status()
        
        print("💙 Welly Always-On Service Status")
        print(f"   Status: {status['systemd_status']}")
        print(f"   Running: {status['service_running']}")
        if status.get("uptime"):
            print(f"   Uptime: {status['uptime']}")
        
        if status["errors"]:
            for error in status["errors"]:
                print(f"   Error: {error}")
    
    elif command == "check":
        prereqs = installer.check_prerequisites()
        
        print("🔍 Checking Prerequisites...")
        print(f"   Existing Welly: {'✅' if prereqs['existing_welly'] else '❌'}")
        print(f"   Database: {'✅' if prereqs['database_exists'] else '❌'}")
        print(f"   Skills: {'✅' if prereqs['skills_available'] else '❌'}")
        print(f"   Python modules: {'✅' if prereqs['python_modules'] else '❌'}")
        print(f"   Systemd: {'✅' if prereqs['systemd_available'] else '❌'}")
        
        if prereqs["errors"]:
            print("\nIssues found:")
            for error in prereqs["errors"]:
                print(f"   ❌ {error}")
        else:
            print("\n✅ All prerequisites satisfied")
    
    elif command == "uninstall":
        print("🗑️ Uninstalling Welly Always-On Service...")
        print("   (This preserves your existing Welly system)")
        
        result = installer.uninstall_service()
        
        for step in result["steps_completed"]:
            print(f"   ✅ {step.replace('_', ' ').title()}")
        
        for error in result["errors"]:
            print(f"   ❌ {error}")
        
        if not result["errors"]:
            print("✅ Always-on service uninstalled. Existing Welly preserved.")
        
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
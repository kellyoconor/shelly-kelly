#!/usr/bin/env python3
"""
Critical Alert System Integration Test

Tests all components of the critical alert safeguard system to ensure
they're working together properly.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime

class CriticalAlertSystemTest:
    def __init__(self):
        self.workspace = "/data/workspace"
        self.test_results = []
        self.test_count = 0
        self.passed_count = 0
        
    def run_command(self, command, cwd=None):
        """Run command and return result"""
        try:
            result = subprocess.run(
                command, shell=True, 
                capture_output=True, text=True, 
                cwd=cwd or self.workspace,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_case(self, name, command, expected_success=True, expected_in_output=None):
        """Run a test case and record results"""
        self.test_count += 1
        print(f"\n[{self.test_count}] Testing: {name}")
        print(f"Command: {command}")
        
        result = self.run_command(command)
        
        success = True
        failure_reason = []
        
        # Check if command succeeded as expected
        if expected_success and not result["success"]:
            success = False
            failure_reason.append(f"Expected success but got error: {result['stderr']}")
        elif not expected_success and result["success"]:
            success = False
            failure_reason.append("Expected failure but command succeeded")
        
        # Check if expected output is present
        if expected_in_output:
            output = result["stdout"] + " " + result["stderr"]
            if expected_in_output.lower() not in output.lower():
                success = False
                failure_reason.append(f"Expected '{expected_in_output}' in output")
        
        if success:
            print("✅ PASSED")
            self.passed_count += 1
            status = "PASSED"
        else:
            print("❌ FAILED")
            for reason in failure_reason:
                print(f"   Reason: {reason}")
            status = "FAILED"
        
        print(f"   Output: {result['stdout'][:100]}{'...' if len(result['stdout']) > 100 else ''}")
        if result["stderr"]:
            print(f"   Stderr: {result['stderr'][:100]}{'...' if len(result['stderr']) > 100 else ''}")
        
        self.test_results.append({
            "name": name,
            "command": command,
            "status": status,
            "output": result["stdout"],
            "error": result["stderr"],
            "failure_reason": failure_reason if not success else None
        })
        
        return success
    
    def test_file_exists(self, name, filepath):
        """Test if required file exists"""
        self.test_count += 1
        print(f"\n[{self.test_count}] Testing: {name}")
        
        full_path = os.path.join(self.workspace, filepath) if not filepath.startswith('/') else filepath
        exists = os.path.exists(full_path)
        
        if exists:
            print("✅ PASSED")
            print(f"   File exists: {full_path}")
            self.passed_count += 1
            status = "PASSED"
        else:
            print("❌ FAILED")
            print(f"   File missing: {full_path}")
            status = "FAILED"
        
        self.test_results.append({
            "name": name,
            "command": f"test -f {full_path}",
            "status": status,
            "output": f"File exists: {exists}",
            "error": "" if exists else f"File not found: {full_path}",
            "failure_reason": None if exists else [f"Required file missing: {full_path}"]
        })
        
        return exists
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("🚨 Critical Alert Safeguard System - Integration Test")
        print("=" * 60)
        
        # Test 1: File Existence Checks
        print("\n📁 TESTING FILE EXISTENCE")
        self.test_file_exists("Critical Alert Engine", "critical-alert-engine.py")
        self.test_file_exists("Netty Urgent Adapter", "netty-urgent-adapter.py")
        self.test_file_exists("Welly Health Monitor", "welly-health-monitor.py")
        self.test_file_exists("Alert Retry Processor", "alert-retry-processor.cjs")
        self.test_file_exists("Alert Configuration", "alert-config.json")
        self.test_file_exists("Updated Heartbeat", "HEARTBEAT.md")
        
        # Test 2: Script Permissions
        print("\n🔒 TESTING SCRIPT PERMISSIONS")
        self.test_case("Critical Alert Engine Executable", 
                      "test -x critical-alert-engine.py",
                      expected_success=True)
        self.test_case("Netty Adapter Executable",
                      "test -x netty-urgent-adapter.py", 
                      expected_success=True)
        self.test_case("Welly Monitor Executable",
                      "test -x welly-health-monitor.py",
                      expected_success=True)
        
        # Test 3: Basic Command Functionality
        print("\n⚙️ TESTING BASIC FUNCTIONALITY")
        self.test_case("Critical Alert Engine Help",
                      "python3 critical-alert-engine.py",
                      expected_success=False,  # Should show usage and exit with error
                      expected_in_output="Usage:")
        
        self.test_case("Alert Retry Processor Help",
                      "node alert-retry-processor.cjs",
                      expected_success=True,
                      expected_in_output="Usage:")
        
        self.test_case("Netty Adapter Help", 
                      "python3 netty-urgent-adapter.py",
                      expected_success=True,
                      expected_in_output="Usage:")
        
        # Test 4: Alert Creation and Management
        print("\n🚨 TESTING ALERT CREATION")
        test_alert_content = "System test alert - please ignore"
        
        self.test_case("Create Test URGENT Alert",
                      f"python3 critical-alert-engine.py create '{test_alert_content}' URGENT test system",
                      expected_success=True,
                      expected_in_output="Created alert")
        
        self.test_case("Check Alert System Status",
                      "python3 critical-alert-engine.py status",
                      expected_success=True,
                      expected_in_output="total_alerts")
        
        self.test_case("Auto-Mark Test Alert as Responded",
                      "python3 critical-alert-engine.py respond 5",
                      expected_success=True)
        
        # Test 5: Integration Components
        print("\n🔗 TESTING INTEGRATION COMPONENTS")
        
        # Test heartbeat integration
        self.test_case("Heartbeat Integration Test",
                      "node alert-retry-processor.cjs heartbeat",
                      expected_success=True)
        
        # Test Netty integration (if pending_checkins.md exists)
        if os.path.exists(os.path.join(self.workspace, "pending_checkins.md")):
            self.test_case("Netty Gap Analysis Test",
                          "python3 netty-urgent-adapter.py analyze",
                          expected_success=True)
        else:
            print("\n[SKIP] Netty integration test - no pending_checkins.md found")
        
        # Test Welly health monitoring
        self.test_case("Welly Health Symptom Test",
                      "python3 welly-health-monitor.py test",
                      expected_success=True,
                      expected_in_output="Test Analysis")
        
        # Test 6: Configuration and Setup
        print("\n📋 TESTING CONFIGURATION")
        
        self.test_case("Check Alert Configuration",
                      "python3 -c \"import json; json.load(open('alert-config.json'))\"",
                      expected_success=True)
        
        # Verify heartbeat was updated with critical alert checks
        self.test_case("Heartbeat Contains Critical Alert Check",
                      "grep -q 'CRITICAL ALERT SYSTEM' HEARTBEAT.md",
                      expected_success=True)
        
        # Test 7: Clean Up Test Data
        print("\n🧹 CLEANING UP TEST DATA")
        self.test_case("Generate Final Status Report",
                      "python3 critical-alert-engine.py report",
                      expected_success=True,
                      expected_in_output="Critical Alert System")
        
        # Generate test report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate final test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {self.test_count}")
        print(f"Passed: {self.passed_count}")
        print(f"Failed: {self.test_count - self.passed_count}")
        print(f"Success Rate: {(self.passed_count/self.test_count*100):.1f}%")
        
        if self.passed_count == self.test_count:
            print("\n🎉 ALL TESTS PASSED! Critical Alert System is ready to use.")
            print("\nNext steps:")
            print("1. Review the setup guide: cat CRITICAL-ALERT-SETUP.md")
            print("2. Monitor system operation during heartbeats")
            print("3. Test with actual urgent scenarios when appropriate")
            
            overall_status = "READY"
        else:
            print("\n⚠️ SOME TESTS FAILED. Review failures before deploying.")
            print("\nFailed tests:")
            for result in self.test_results:
                if result["status"] == "FAILED":
                    print(f"- {result['name']}")
                    if result["failure_reason"]:
                        for reason in result["failure_reason"]:
                            print(f"  • {reason}")
            
            overall_status = "NEEDS_ATTENTION"
        
        # Write detailed test report to file
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        report_file = f"test-results-{timestamp}.json"
        
        full_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": self.test_count,
                "passed": self.passed_count,
                "failed": self.test_count - self.passed_count,
                "success_rate": round(self.passed_count/self.test_count*100, 1),
                "overall_status": overall_status
            },
            "test_details": self.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"\nDetailed test report saved to: {report_file}")
        print("\n🛡️ Critical Alert Safeguard System Testing Complete")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Critical Alert System Integration Test")
        print("Usage: python3 test-critical-alert-system.py")
        print("\nThis script tests all components of the critical alert safeguard system.")
        return
    
    # Change to workspace directory
    os.chdir('/data/workspace')
    
    # Run the complete test suite
    tester = CriticalAlertSystemTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
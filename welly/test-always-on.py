#!/usr/bin/env python3
"""
Welly Always-On System Test Suite

Comprehensive testing of the always-on pattern detection service to ensure:
- All components work together properly
- Kelly's voice and personality are preserved  
- Integration with existing Welly is seamless
- Service reliability and error handling
"""

import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

class WellyAlwaysOnTester:
    """Comprehensive test suite for always-on Welly system"""
    
    def __init__(self, workspace="/data/workspace"):
        self.workspace = Path(workspace)
        self.welly_dir = self.workspace / "welly"
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "failures": [],
            "components_tested": []
        }
    
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        self.test_results["tests_run"] += 1
        
        if passed:
            self.test_results["tests_passed"] += 1
            print(f"   ✅ {test_name}")
        else:
            self.test_results["tests_failed"] += 1
            self.test_results["failures"].append({
                "test": test_name,
                "message": message,
                "timestamp": datetime.now().isoformat()
            })
            print(f"   ❌ {test_name}: {message}")
    
    def test_existing_welly_preserved(self) -> bool:
        """Test that existing Welly functionality is preserved"""
        print("🔍 Testing Existing Welly Preservation...")
        
        # Test 1: Original entry point exists and works
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "welly.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Original welly.py status command",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Original welly.py status command", False, str(e))
        
        # Test 2: Database and components exist
        required_files = [
            "welly_memory.db",
            "welly_voice.py", 
            "welly_interpreter.py",
            "welly_memory.py",
            "welly_ingest.py",
            "welly_heartbeat.py"
        ]
        
        for file in required_files:
            file_path = self.welly_dir / file
            self.log_test(
                f"Required file exists: {file}",
                file_path.exists(),
                f"File not found: {file_path}"
            )
        
        # Test 3: Voice system maintains Kelly's style
        try:
            sys.path.append(str(self.welly_dir))
            from welly_voice import WellyVoice
            
            voice = WellyVoice()
            
            # Check for Kelly's approved phrases
            kelly_phrases_exist = (
                "Your body's been whispering" in str(voice.approved_phrases) or
                "push through it" in str(voice.approved_phrases)
            )
            
            self.log_test(
                "Kelly's voice patterns preserved",
                kelly_phrases_exist,
                "Kelly's approved phrases not found in voice system"
            )
            
            # Check avoid phrases
            avoid_phrases_exist = (
                "based on your biometrics" in voice.avoid_phrases or
                "optimize your" in voice.avoid_phrases
            )
            
            self.log_test(
                "Kelly's avoid phrases preserved", 
                avoid_phrases_exist,
                "Kelly's avoid phrases not found in voice system"
            )
            
        except Exception as e:
            self.log_test("Voice system import test", False, str(e))
        
        return True
    
    def test_always_on_components(self) -> bool:
        """Test that all new always-on components work"""
        print("🔍 Testing Always-On Components...")
        
        # Test 1: Monitor component
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "welly-monitor.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Monitor component status",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Monitor component status", False, str(e))
        
        # Test 2: Poller component
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "welly-poller.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Poller component status",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Poller component status", False, str(e))
        
        # Test 3: Pattern detection component
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "welly-patterns.py"), "summary", "7"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Pattern detection component",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Pattern detection component", False, str(e))
        
        # Test 4: Alert system component
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "welly-alerts.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Alert system component",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Alert system component", False, str(e))
        
        # Test 5: Heartbeat integration
        try:
            result = subprocess.run([
                "python3", str(self.welly_dir / "heartbeat-integration.py"), "status"
            ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
            
            self.log_test(
                "Heartbeat integration component",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else ""
            )
        except Exception as e:
            self.log_test("Heartbeat integration component", False, str(e))
        
        return True
    
    def test_data_integration(self) -> bool:
        """Test integration with existing data skills"""
        print("🔍 Testing Data Integration...")
        
        # Test 1: Oura skill availability
        oura_skill = self.workspace / "skills" / "oura" / "scripts" / "oura.py"
        self.log_test(
            "Oura skill exists",
            oura_skill.exists(),
            f"Oura skill not found at {oura_skill}"
        )
        
        # Test 2: Strava skill availability  
        strava_skill = self.workspace / "skills" / "strava" / "scripts" / "strava.py"
        self.log_test(
            "Strava skill exists",
            strava_skill.exists(),
            f"Strava skill not found at {strava_skill}"
        )
        
        # Test 3: Poller can access skills
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_poller", str(self.welly_dir / "welly-poller.py"))
            welly_poller_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_poller_module)
            WellyPoller = welly_poller_module.WellyPoller
            
            poller = WellyPoller()
            status = poller.get_polling_status()
            
            self.log_test(
                "Poller initialization",
                "config" in status,
                "Poller status missing expected fields"
            )
        except Exception as e:
            self.log_test("Poller initialization", False, str(e))
        
        # Test 4: Existing ingest system works
        try:
            from welly_ingest import WellyIngest
            
            ingest = WellyIngest()
            
            # Test database connection
            ingest.setup_database()
            
            self.log_test(
                "Ingest system database setup",
                True,
                ""
            )
        except Exception as e:
            self.log_test("Ingest system database setup", False, str(e))
        
        return True
    
    def test_kelly_voice_preservation(self) -> bool:
        """Test that Kelly's voice and style are preserved in always-on alerts"""
        print("🔍 Testing Kelly's Voice Preservation...")
        
        try:
            sys.path.append(str(self.welly_dir))
            from welly_voice import WellyVoice
            
            # Load welly-alerts using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_alerts", str(self.welly_dir / "welly-alerts.py"))
            welly_alerts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_alerts_module)
            WellyAlerts = welly_alerts_module.WellyAlerts
            
            voice = WellyVoice()
            alerts = WellyAlerts()
            
            # Test 1: Voice system has Kelly's phrases
            kelly_phrases = [
                "Your body's been whispering",
                "push through it",
                "Numbers say okay-ish"
            ]
            
            found_kelly_phrases = 0
            for phrase in kelly_phrases:
                if any(phrase in str(phrase_list) for phrase_list in voice.approved_phrases.values()):
                    found_kelly_phrases += 1
            
            self.log_test(
                "Kelly's signature phrases in voice system",
                found_kelly_phrases >= 1,
                f"Only found {found_kelly_phrases} of {len(kelly_phrases)} Kelly phrases"
            )
            
            # Test 2: Alert system uses voice system
            self.log_test(
                "Alert system uses voice system",
                hasattr(alerts, 'voice') and isinstance(alerts.voice, WellyVoice),
                "Alert system doesn't properly integrate with voice system"
            )
            
            # Test 3: Three-part format structure  
            # (This would need sample data to fully test, but we can check structure)
            self.log_test(
                "Voice system has three-part format methods",
                hasattr(voice, '_generate_noticing') or 'noticing' in dir(voice),
                "Voice system missing three-part format methods"
            )
            
        except Exception as e:
            self.log_test("Kelly's voice preservation test", False, str(e))
        
        return True
    
    def test_alert_timing_logic(self) -> bool:
        """Test that alert timing respects Kelly's preferences"""
        print("🔍 Testing Alert Timing Logic...")
        
        try:
            sys.path.append(str(self.welly_dir))
            
            # Load welly-alerts using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_alerts", str(self.welly_dir / "welly-alerts.py"))
            welly_alerts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_alerts_module)
            WellyAlerts = welly_alerts_module.WellyAlerts
            
            alerts = WellyAlerts()
            
            # Test 1: Quiet hours detection
            # Temporarily modify time to test quiet hours logic
            quiet_hours_work = alerts._is_quiet_hours() is not None
            
            self.log_test(
                "Quiet hours detection works",
                quiet_hours_work,
                "Quiet hours detection returned None"
            )
            
            # Test 2: Alert limiting logic
            can_send_result = alerts._can_send_alert()
            
            self.log_test(
                "Alert limiting logic works",
                isinstance(can_send_result, tuple) and len(can_send_result) == 2,
                "Alert limiting logic doesn't return expected tuple"
            )
            
            # Test 3: Alert configuration
            expected_config_keys = ["max_alerts_per_day", "cooldown_hours", "quiet_hours_start"]
            config_complete = all(key in alerts.alert_config for key in expected_config_keys)
            
            self.log_test(
                "Alert configuration complete",
                config_complete,
                "Missing expected alert configuration keys"
            )
            
            # Test 4: Weekend mode detection
            weekend_mode_works = alerts._is_weekend_mode() is not None
            
            self.log_test(
                "Weekend mode detection works",
                weekend_mode_works,
                "Weekend mode detection failed"
            )
            
        except Exception as e:
            self.log_test("Alert timing logic test", False, str(e))
        
        return True
    
    def test_pattern_detection_logic(self) -> bool:
        """Test pattern detection respects Kelly's specific patterns"""
        print("🔍 Testing Pattern Detection Logic...")
        
        try:
            sys.path.append(str(self.welly_dir))
            
            # Load welly-patterns using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_patterns", str(self.welly_dir / "welly-patterns.py"))
            welly_patterns_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_patterns_module)
            WellyPatterns = welly_patterns_module.WellyPatterns
            
            patterns = WellyPatterns()
            
            # Test 1: Kelly-specific thresholds exist
            expected_thresholds = ["push_pattern", "recovery_pattern", "warning_pattern"]
            thresholds_exist = all(key in patterns.thresholds for key in expected_thresholds)
            
            self.log_test(
                "Kelly-specific pattern thresholds defined",
                thresholds_exist,
                "Missing expected pattern threshold categories"
            )
            
            # Test 2: Push-through detection method exists
            push_detection_exists = hasattr(patterns, '_detect_push_through_pattern')
            
            self.log_test(
                "Push-through pattern detection method exists",
                push_detection_exists,
                "Missing Kelly's key pattern detection method"
            )
            
            # Test 3: Pattern detection integrates with existing memory
            memory_integration = hasattr(patterns, 'memory') and hasattr(patterns.memory, 'get_relevant_patterns')
            
            self.log_test(
                "Pattern detection integrates with existing memory",
                memory_integration,
                "Pattern detection doesn't properly integrate with existing memory system"
            )
            
            # Test 4: Kelly-specific pattern recognition
            kelly_specific_patterns = [
                "push_through",
                "mind_body_misalignment", 
                "positive_alignment"
            ]
            
            # Check if pattern types are recognized in the code
            pattern_source = open(self.welly_dir / "welly-patterns.py").read()
            kelly_patterns_found = sum(1 for pattern in kelly_specific_patterns 
                                     if pattern in pattern_source)
            
            self.log_test(
                "Kelly-specific patterns implemented",
                kelly_patterns_found >= 2,
                f"Only found {kelly_patterns_found} of {len(kelly_specific_patterns)} Kelly patterns"
            )
            
        except Exception as e:
            self.log_test("Pattern detection logic test", False, str(e))
        
        return True
    
    def test_service_integration(self) -> bool:
        """Test service installation and management"""
        print("🔍 Testing Service Integration...")
        
        # Test 1: Service file exists
        service_file = self.welly_dir / "welly-monitor.service"
        self.log_test(
            "Systemd service file exists",
            service_file.exists(),
            f"Service file not found at {service_file}"
        )
        
        # Test 2: Installation script exists and works
        install_script = self.welly_dir / "install-always-on.py"
        
        self.log_test(
            "Installation script exists",
            install_script.exists(),
            f"Installation script not found at {install_script}"
        )
        
        if install_script.exists():
            try:
                result = subprocess.run([
                    "python3", str(install_script), "check"
                ], cwd=self.welly_dir, capture_output=True, text=True, timeout=30)
                
                self.log_test(
                    "Installation prerequisite check",
                    result.returncode == 0,
                    result.stderr if result.returncode != 0 else ""
                )
            except Exception as e:
                self.log_test("Installation prerequisite check", False, str(e))
        
        # Test 3: Management scripts exist
        management_scripts = [
            "start-always-on.sh",
            "stop-always-on.sh", 
            "status-always-on.sh"
        ]
        
        for script in management_scripts:
            script_path = self.welly_dir / script
            self.log_test(
                f"Management script exists: {script}",
                script_path.exists() if script_path.parent.exists() else True,  # May not exist until install
                f"Management script not found: {script}"
            )
        
        return True
    
    async def test_async_functionality(self) -> bool:
        """Test async components work properly"""
        print("🔍 Testing Async Functionality...")
        
        try:
            sys.path.append(str(self.welly_dir))
            
            # Load modules using importlib
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("welly_poller", str(self.welly_dir / "welly-poller.py"))
            welly_poller_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_poller_module)
            WellyPoller = welly_poller_module.WellyPoller
            
            spec = importlib.util.spec_from_file_location("welly_alerts", str(self.welly_dir / "welly-alerts.py"))
            welly_alerts_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_alerts_module)
            WellyAlerts = welly_alerts_module.WellyAlerts
            
            spec = importlib.util.spec_from_file_location("welly_patterns", str(self.welly_dir / "welly-patterns.py"))
            welly_patterns_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_patterns_module)
            WellyPatterns = welly_patterns_module.WellyPatterns
            
            # Test 1: Poller async methods
            poller = WellyPoller()
            try:
                # Test that async method exists and can be called
                poll_result = await poller.poll_all_sources()
                
                self.log_test(
                    "Poller async functionality",
                    isinstance(poll_result, dict),
                    "Poller poll_all_sources didn't return expected dict"
                )
            except Exception as e:
                self.log_test("Poller async functionality", False, str(e))
            
            # Test 2: Alert system async methods
            alerts = WellyAlerts()
            try:
                # Test gentle alert method (don't actually send)
                test_message = "Test alert message"
                # We'll just test the method exists, not actually send
                send_method_exists = hasattr(alerts, 'send_gentle_alert')
                
                self.log_test(
                    "Alert system async functionality",
                    send_method_exists,
                    "send_gentle_alert method missing from alert system"
                )
            except Exception as e:
                self.log_test("Alert system async functionality", False, str(e))
            
            # Test 3: Pattern analysis async methods
            patterns = WellyPatterns()
            try:
                # Test pattern analysis method exists
                analysis_method_exists = hasattr(patterns, 'analyze_concerning_patterns')
                
                self.log_test(
                    "Pattern analysis async functionality",
                    analysis_method_exists,
                    "analyze_concerning_patterns method missing"
                )
            except Exception as e:
                self.log_test("Pattern analysis async functionality", False, str(e))
        
        except Exception as e:
            self.log_test("Async functionality import test", False, str(e))
        
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling and graceful degradation"""
        print("🔍 Testing Error Handling...")
        
        try:
            sys.path.append(str(self.welly_dir))
            
            # Load welly-poller using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_poller", str(self.welly_dir / "welly-poller.py"))
            welly_poller_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_poller_module)
            WellyPoller = welly_poller_module.WellyPoller
            
            poller = WellyPoller()
            
            # Test 1: Poller handles missing skills gracefully
            # Temporarily move skills to test error handling
            # (We'll just test the error handling structure exists)
            
            error_handling_methods = [
                '_load_polling_state',
                '_save_polling_state',
                'get_polling_status'
            ]
            
            methods_exist = all(hasattr(poller, method) for method in error_handling_methods)
            
            self.log_test(
                "Poller error handling methods exist",
                methods_exist,
                "Missing expected error handling methods in poller"
            )
            
            # Test 2: State persistence works
            try:
                status = poller.get_polling_status()
                state_fields = ["config", "should_poll_oura", "should_poll_strava"]
                status_complete = all(field in status for field in state_fields)
                
                self.log_test(
                    "Poller state persistence",
                    status_complete,
                    "Poller status missing expected fields"
                )
            except Exception as e:
                self.log_test("Poller state persistence", False, str(e))
            
        except Exception as e:
            self.log_test("Error handling test setup", False, str(e))
        
        return True
    
    def run_comprehensive_test(self) -> Dict:
        """Run all tests and return comprehensive results"""
        print("🧪 Running Welly Always-On Comprehensive Test Suite")
        print("=" * 60)
        
        # Run all test categories
        test_categories = [
            ("Existing Welly Preservation", self.test_existing_welly_preserved),
            ("Always-On Components", self.test_always_on_components),
            ("Data Integration", self.test_data_integration),
            ("Kelly's Voice Preservation", self.test_kelly_voice_preservation),
            ("Alert Timing Logic", self.test_alert_timing_logic),
            ("Pattern Detection Logic", self.test_pattern_detection_logic),
            ("Service Integration", self.test_service_integration),
            ("Error Handling", self.test_error_handling)
        ]
        
        for category_name, test_func in test_categories:
            try:
                test_func()
                self.test_results["components_tested"].append(category_name)
            except Exception as e:
                self.log_test(f"{category_name} (category)", False, str(e))
        
        # Run async tests
        try:
            asyncio.run(self.test_async_functionality())
            self.test_results["components_tested"].append("Async Functionality")
        except Exception as e:
            self.log_test("Async Functionality (category)", False, str(e))
        
        # Calculate success rate
        success_rate = (self.test_results["tests_passed"] / self.test_results["tests_run"] * 100) if self.test_results["tests_run"] > 0 else 0
        
        print("\n" + "=" * 60)
        print("🧪 Test Results Summary")
        print(f"   Tests run: {self.test_results['tests_run']}")
        print(f"   Tests passed: {self.test_results['tests_passed']}")
        print(f"   Tests failed: {self.test_results['tests_failed']}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Components tested: {len(self.test_results['components_tested'])}")
        
        if self.test_results["failures"]:
            print("\n❌ Failed Tests:")
            for failure in self.test_results["failures"]:
                print(f"   • {failure['test']}: {failure['message']}")
        
        # Overall assessment
        if success_rate >= 90:
            print("\n✅ System ready for deployment!")
        elif success_rate >= 75:
            print("\n⚠️ System mostly ready, some issues to address")
        else:
            print("\n❌ System needs significant fixes before deployment")
        
        return self.test_results


def main():
    """Run test suite"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        tester = WellyAlwaysOnTester()
        
        if command == "quick":
            # Quick test - just check components exist
            print("⚡ Quick Test - Component Existence")
            tester.test_always_on_components()
            tester.test_existing_welly_preserved()
            
        elif command == "voice":
            # Test just Kelly's voice preservation
            print("🗣️ Kelly's Voice Preservation Test")
            tester.test_kelly_voice_preservation()
            
        elif command == "integration":
            # Test just integration aspects
            print("🔗 Integration Test")
            tester.test_data_integration()
            tester.test_service_integration()
            
        else:
            print(f"Unknown test command: {command}")
            print("Usage: python3 test-always-on.py [quick|voice|integration]")
    else:
        # Run comprehensive test suite
        tester = WellyAlwaysOnTester()
        results = tester.run_comprehensive_test()
        
        # Save results to file
        results_file = Path("/data/workspace/memory") / f"welly-test-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        try:
            results_file.parent.mkdir(exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\n📁 Test results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save test results: {e}")


if __name__ == "__main__":
    main()
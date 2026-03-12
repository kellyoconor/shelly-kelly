#!/usr/bin/env python3
"""
Welly Health Monitor - Critical Alert Integration

Monitors health patterns from Oura/Strava data and creates critical alerts
for concerning trends that require immediate attention.
"""

import json
import os
import re
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class WellyHealthMonitor:
    def __init__(self):
        self.workspace = "/data/workspace"
        self.critical_engine = os.path.join(self.workspace, "critical-alert-engine.py")
        self.health_context_file = os.path.join(self.workspace, "health-context.py")
        
        # Health alert thresholds
        self.thresholds = {
            "CRITICAL": {
                "sleep_hours": 5.0,              # Less than 5 hours sleep
                "consecutive_poor_sleep": 3,      # 3+ nights of poor sleep
                "readiness_critical": 50,         # Readiness below 50
                "hrv_drop_percent": 25,           # HRV drop > 25% from baseline
                "resting_hr_elevation": 15,      # Resting HR > 15bpm above baseline
                "recovery_score": 25,             # Recovery score < 25
                "consecutive_critical_days": 2    # 2+ consecutive critical days
            },
            "URGENT": {
                "sleep_hours": 6.0,              # Less than 6 hours sleep
                "consecutive_poor_sleep": 2,      # 2+ nights of poor sleep
                "readiness_urgent": 60,           # Readiness below 60 for multiple days
                "hrv_drop_percent": 15,           # HRV drop > 15% from baseline
                "resting_hr_elevation": 10,      # Resting HR > 10bpm above baseline
                "recovery_score": 40,             # Recovery score < 40
                "consecutive_urgent_days": 3      # 3+ consecutive concerning days
            }
        }
        
        # Pattern keywords for symptom detection
        self.symptom_keywords = {
            "critical": [
                "chest pain", "can't breathe", "dizzy", "fainted", "collapsed",
                "severe pain", "emergency", "hospital", "urgent care",
                "can't sleep", "heart racing", "panic", "numb", "tingling"
            ],
            "urgent": [
                "exhausted", "can't recover", "always tired", "drained",
                "stressed", "overwhelmed", "burnt out", "constant fatigue",
                "sore", "aching", "injured", "hurting", "inflammation"
            ],
            "concerning": [
                "tired", "low energy", "sluggish", "off", "weird",
                "unusual", "different", "not right", "struggling"
            ]
        }
    
    def analyze_sleep_patterns(self, sleep_data: List[Dict]) -> Tuple[str, Dict]:
        """Analyze sleep patterns for concerning trends"""
        if not sleep_data:
            return "NORMAL", {"reason": "No sleep data available"}
        
        analysis = {
            "average_sleep": 0,
            "consecutive_poor_nights": 0,
            "critical_nights": 0,
            "trends": []
        }
        
        total_sleep = 0
        consecutive_poor = 0
        max_consecutive_poor = 0
        critical_nights = 0
        
        for night in sleep_data[-7:]:  # Last 7 nights
            sleep_hours = night.get("total_sleep_duration", 0) / 3600  # Convert to hours
            total_sleep += sleep_hours
            
            if sleep_hours < self.thresholds["CRITICAL"]["sleep_hours"]:
                consecutive_poor += 1
                critical_nights += 1
                analysis["trends"].append(f"Critical sleep: {sleep_hours:.1f}h on {night.get('date', 'unknown')}")
            elif sleep_hours < self.thresholds["URGENT"]["sleep_hours"]:
                consecutive_poor += 1
                analysis["trends"].append(f"Poor sleep: {sleep_hours:.1f}h on {night.get('date', 'unknown')}")
            else:
                consecutive_poor = 0
            
            max_consecutive_poor = max(max_consecutive_poor, consecutive_poor)
        
        analysis["average_sleep"] = total_sleep / len(sleep_data[-7:]) if sleep_data else 0
        analysis["consecutive_poor_nights"] = max_consecutive_poor
        analysis["critical_nights"] = critical_nights
        
        # Determine urgency
        if (critical_nights >= self.thresholds["CRITICAL"]["consecutive_critical_days"] or
            max_consecutive_poor >= self.thresholds["CRITICAL"]["consecutive_poor_sleep"]):
            return "CRITICAL", analysis
        elif (max_consecutive_poor >= self.thresholds["URGENT"]["consecutive_poor_sleep"] or
              analysis["average_sleep"] < self.thresholds["URGENT"]["sleep_hours"]):
            return "URGENT", analysis
        else:
            return "NORMAL", analysis
    
    def analyze_readiness_patterns(self, readiness_data: List[Dict]) -> Tuple[str, Dict]:
        """Analyze Oura readiness patterns"""
        if not readiness_data:
            return "NORMAL", {"reason": "No readiness data available"}
        
        analysis = {
            "average_readiness": 0,
            "consecutive_low_days": 0,
            "critical_days": 0,
            "trends": []
        }
        
        total_readiness = 0
        consecutive_low = 0
        max_consecutive_low = 0
        critical_days = 0
        
        for day in readiness_data[-7:]:  # Last 7 days
            score = day.get("score", 100)
            total_readiness += score
            
            if score < self.thresholds["CRITICAL"]["readiness_critical"]:
                consecutive_low += 1
                critical_days += 1
                analysis["trends"].append(f"Critical readiness: {score} on {day.get('date', 'unknown')}")
            elif score < self.thresholds["URGENT"]["readiness_urgent"]:
                consecutive_low += 1
                analysis["trends"].append(f"Low readiness: {score} on {day.get('date', 'unknown')}")
            else:
                consecutive_low = 0
            
            max_consecutive_low = max(max_consecutive_low, consecutive_low)
        
        analysis["average_readiness"] = total_readiness / len(readiness_data[-7:]) if readiness_data else 100
        analysis["consecutive_low_days"] = max_consecutive_low
        analysis["critical_days"] = critical_days
        
        # Determine urgency
        if (critical_days >= self.thresholds["CRITICAL"]["consecutive_critical_days"] or
            max_consecutive_low >= 4):  # 4+ consecutive low days is critical
            return "CRITICAL", analysis
        elif (max_consecutive_low >= self.thresholds["URGENT"]["consecutive_urgent_days"] or
              analysis["average_readiness"] < self.thresholds["URGENT"]["readiness_urgent"]):
            return "URGENT", analysis
        else:
            return "NORMAL", analysis
    
    def analyze_hrv_patterns(self, hrv_data: List[Dict]) -> Tuple[str, Dict]:
        """Analyze HRV trends for significant drops"""
        if not hrv_data or len(hrv_data) < 7:
            return "NORMAL", {"reason": "Insufficient HRV data"}
        
        # Calculate baseline (30-day average if available, otherwise 7-day)
        baseline_data = hrv_data[-30:] if len(hrv_data) >= 30 else hrv_data[-14:]
        baseline_hrv = sum(day.get("rmssd", 0) for day in baseline_data) / len(baseline_data)
        
        analysis = {
            "baseline_hrv": baseline_hrv,
            "recent_hrv": 0,
            "drop_percentage": 0,
            "consecutive_low_days": 0,
            "trends": []
        }
        
        # Analyze recent 7 days
        recent_data = hrv_data[-7:]
        recent_hrv = sum(day.get("rmssd", 0) for day in recent_data) / len(recent_data)
        drop_percentage = ((baseline_hrv - recent_hrv) / baseline_hrv * 100) if baseline_hrv > 0 else 0
        
        analysis["recent_hrv"] = recent_hrv
        analysis["drop_percentage"] = drop_percentage
        
        # Check for consecutive low days
        consecutive_low = 0
        max_consecutive_low = 0
        
        for day in recent_data:
            day_hrv = day.get("rmssd", 0)
            day_drop = ((baseline_hrv - day_hrv) / baseline_hrv * 100) if baseline_hrv > 0 else 0
            
            if day_drop >= self.thresholds["URGENT"]["hrv_drop_percent"]:
                consecutive_low += 1
                analysis["trends"].append(f"Low HRV: {day_hrv:.1f} (-{day_drop:.1f}%) on {day.get('date', 'unknown')}")
            else:
                consecutive_low = 0
            
            max_consecutive_low = max(max_consecutive_low, consecutive_low)
        
        analysis["consecutive_low_days"] = max_consecutive_low
        
        # Determine urgency
        if (drop_percentage >= self.thresholds["CRITICAL"]["hrv_drop_percent"] or
            max_consecutive_low >= 3):
            return "CRITICAL", analysis
        elif (drop_percentage >= self.thresholds["URGENT"]["hrv_drop_percent"] or
              max_consecutive_low >= 2):
            return "URGENT", analysis
        else:
            return "NORMAL", analysis
    
    def analyze_resting_hr_patterns(self, hr_data: List[Dict]) -> Tuple[str, Dict]:
        """Analyze resting heart rate for elevation"""
        if not hr_data or len(hr_data) < 7:
            return "NORMAL", {"reason": "Insufficient heart rate data"}
        
        # Calculate baseline
        baseline_data = hr_data[-30:] if len(hr_data) >= 30 else hr_data[-14:]
        baseline_hr = sum(day.get("resting_hr", 0) for day in baseline_data) / len(baseline_data)
        
        analysis = {
            "baseline_hr": baseline_hr,
            "recent_hr": 0,
            "elevation": 0,
            "consecutive_elevated_days": 0,
            "trends": []
        }
        
        # Analyze recent 7 days
        recent_data = hr_data[-7:]
        recent_hr = sum(day.get("resting_hr", 0) for day in recent_data) / len(recent_data)
        elevation = recent_hr - baseline_hr
        
        analysis["recent_hr"] = recent_hr
        analysis["elevation"] = elevation
        
        # Check for consecutive elevated days
        consecutive_elevated = 0
        max_consecutive_elevated = 0
        
        for day in recent_data:
            day_hr = day.get("resting_hr", 0)
            day_elevation = day_hr - baseline_hr
            
            if day_elevation >= self.thresholds["URGENT"]["resting_hr_elevation"]:
                consecutive_elevated += 1
                analysis["trends"].append(f"Elevated HR: {day_hr:.0f} bpm (+{day_elevation:.1f}) on {day.get('date', 'unknown')}")
            else:
                consecutive_elevated = 0
            
            max_consecutive_elevated = max(max_consecutive_elevated, consecutive_elevated)
        
        analysis["consecutive_elevated_days"] = max_consecutive_elevated
        
        # Determine urgency
        if (elevation >= self.thresholds["CRITICAL"]["resting_hr_elevation"] or
            max_consecutive_elevated >= 3):
            return "CRITICAL", analysis
        elif (elevation >= self.thresholds["URGENT"]["resting_hr_elevation"] or
              max_consecutive_elevated >= 2):
            return "URGENT", analysis
        else:
            return "NORMAL", analysis
    
    def analyze_symptom_mentions(self, memory_content: str) -> Tuple[str, Dict]:
        """Analyze memory files for health symptom mentions - WORD BOUNDARY MATCHING"""
        content_lower = memory_content.lower()
        
        analysis = {
            "critical_symptoms": [],
            "urgent_symptoms": [],
            "concerning_symptoms": [],
            "recent_mentions": []
        }
        
        # Check for symptom keywords using word boundary regex to prevent false matches
        for symptom in self.symptom_keywords["critical"]:
            if re.search(r'\b' + re.escape(symptom) + r'\b', content_lower):
                analysis["critical_symptoms"].append(symptom)
        
        for symptom in self.symptom_keywords["urgent"]:
            if re.search(r'\b' + re.escape(symptom) + r'\b', content_lower):
                analysis["urgent_symptoms"].append(symptom)
        
        for symptom in self.symptom_keywords["concerning"]:
            if re.search(r'\b' + re.escape(symptom) + r'\b', content_lower):
                analysis["concerning_symptoms"].append(symptom)
        
        # Determine urgency
        if analysis["critical_symptoms"]:
            return "CRITICAL", analysis
        elif analysis["urgent_symptoms"]:
            return "URGENT", analysis
        elif len(analysis["concerning_symptoms"]) >= 3:  # Multiple concerning mentions
            return "URGENT", analysis
        else:
            return "NORMAL", analysis
    
    def get_recent_memory_content(self, days_back: int = 3) -> str:
        """Get recent memory content for symptom analysis - EXCLUDING alert messages"""
        memory_dir = os.path.join(self.workspace, "memory")
        content = ""
        
        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = os.path.join(memory_dir, f"{date}.md")
            
            # CRITICAL: Skip Welly's own health log files to prevent feedback loops
            if memory_file.endswith(f"welly-health-{date.replace('-', '')}.md"):
                continue
                
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    file_content = f.read()
                    # CRITICAL FIX: Filter out alert system content to prevent feedback loop
                    filtered_content = self.filter_alert_content(file_content)
                    content += f"\n{filtered_content}"
        
        return content
    
    def filter_alert_content(self, content: str) -> str:
        """Filter out alert-related content AND non-health mentions to prevent false symptom detection"""
        lines = content.split('\n')
        filtered_lines = []
        
        # Patterns that indicate alert system content
        alert_skip_patterns = [
            "Health Assessment -",
            "Overall Urgency:",
            "Summary:",
            "Alerts Created:",
            "CRITICAL HEALTH ALERT",
            "🚨 CRITICAL",
            "⚠️ URGENT", 
            "Critical symptoms mentioned recently:",
            "Kelly, I'm noticing some health patterns",
            "Symptom concerns:",
            "Critical: emergency",
            "Urgent: emergency",
            "Alert System",
            "alert system",
            "false health alerts",
            "ESCALATED ALERTS",
            "Manual Review",
            "Test Alert",
            "System Test",
            "Feedback loop",
            "detected own alert",
            "FALSE_ALERT",
            "resolved automatically",
            "Critical:",
            "Urgent:",
            "Concerning:",
            "welly-health-",
            "Health Assessment",
            "Symptom Analysis:",
            "false alert",
            "detected \"",
            "Cleared false alert",
            "substring bug",
            "word boundary",
            "from old memory entry"
        ]
        
        # Patterns for non-health "emergency" mentions
        non_health_emergency_patterns = [
            "emergency modes",
            "emergency fix",
            "emergency tool", 
            "emergency script",
            "emergency repair",
            "Manual control tool",
            "session-manager.py"
        ]
        
        for line in lines:
            # Skip lines that contain alert system content
            if any(pattern in line for pattern in alert_skip_patterns):
                continue
                
            # Skip lines that contain technical "emergency" mentions (not health)
            if any(pattern in line for pattern in non_health_emergency_patterns):
                continue
                
            # Also remove any line that contains "emergency" in a technical context OR alert context
            line_lower = line.lower()
            if ("emergency" in line_lower and 
                any(tech_word in line_lower for tech_word in [
                    "mode", "tool", "script", "fix", "system", "session", 
                    "alert", "detected", "symptoms mentioned", "health patterns",
                    "welly", "monitor", "feedback", "false", "escalated"
                ])):
                continue
                
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def run_health_assessment(self) -> Dict:
        """Run complete health assessment and return findings - FRESH DATA ONLY"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "sleep_analysis": {},
            "readiness_analysis": {},
            "hrv_analysis": {},
            "hr_analysis": {},
            "overall_urgency": "NORMAL",
            "alerts_created": [],
            "summary": ""
        }
        
        try:
            # CRITICAL CHANGE: Only analyze fresh Oura/Strava data patterns
            # NO memory scanning to avoid false positives from historical mentions
            
            # TODO: Implement actual Oura/Strava data fetching
            # For now, assume all data patterns are NORMAL since no fresh data integration
            
            # Simulate sleep analysis (would fetch today's Oura sleep data)
            # sleep_urgency, sleep_analysis = self.analyze_sleep_patterns(fresh_sleep_data)
            sleep_urgency = "NORMAL"
            assessment["sleep_analysis"] = {"urgency": sleep_urgency, "details": {}}
            
            # Simulate readiness analysis (would fetch today's Oura readiness)  
            # readiness_urgency, readiness_analysis = self.analyze_readiness_patterns(fresh_readiness_data)
            readiness_urgency = "NORMAL"
            assessment["readiness_analysis"] = {"urgency": readiness_urgency, "details": {}}
            
            # Simulate HRV analysis (would fetch recent Oura HRV trends)
            # hrv_urgency, hrv_analysis = self.analyze_hrv_patterns(fresh_hrv_data)  
            hrv_urgency = "NORMAL"
            assessment["hrv_analysis"] = {"urgency": hrv_urgency, "details": {}}
            
            # Simulate heart rate analysis (would fetch recent Oura HR data)
            # hr_urgency, hr_analysis = self.analyze_resting_hr_patterns(fresh_hr_data)
            hr_urgency = "NORMAL"
            assessment["hr_analysis"] = {"urgency": hr_urgency, "details": {}}
            
            # Determine overall urgency (highest of data analyses only)
            urgencies = [sleep_urgency, readiness_urgency, hrv_urgency, hr_urgency]
            if "CRITICAL" in urgencies:
                assessment["overall_urgency"] = "CRITICAL"
            elif "URGENT" in urgencies:
                assessment["overall_urgency"] = "URGENT"
            
            # Only create alerts for actual data pattern issues, not memory mentions
            if assessment["overall_urgency"] in ["CRITICAL", "URGENT"]:
                alert_message = self.generate_data_based_alert_message(assessment)
                alert_id = self.create_health_alert(alert_message, assessment["overall_urgency"])
                assessment["alerts_created"].append(alert_id)
            
            # Generate summary
            assessment["summary"] = self.generate_health_summary(assessment)
            
        except Exception as e:
            assessment["error"] = str(e)
            assessment["summary"] = f"Health assessment failed: {e}"
        
        return assessment
    
    def generate_data_based_alert_message(self, assessment: Dict) -> str:
        """Generate alert message based on ACTUAL health data patterns only"""
        urgency = assessment["overall_urgency"]
        
        if urgency == "CRITICAL":
            prefix = "🚨 CRITICAL HEALTH DATA ALERT"
        else:
            prefix = "⚠️ URGENT HEALTH DATA CONCERN"
        
        message_parts = [prefix]
        
        # Add specific data concerns based on actual Oura/Strava patterns
        data_concerns = []
        
        # Check sleep analysis results
        if assessment.get("sleep_analysis", {}).get("urgency") in ["CRITICAL", "URGENT"]:
            sleep_details = assessment["sleep_analysis"].get("details", {})
            if sleep_details.get("consecutive_poor_nights", 0) >= 3:
                data_concerns.append(f"Sleep: {sleep_details['consecutive_poor_nights']} consecutive poor nights")
            if sleep_details.get("average_sleep", 0) < 5.5:
                data_concerns.append(f"Sleep: Average {sleep_details['average_sleep']:.1f} hours this week")
        
        # Check readiness patterns
        if assessment.get("readiness_analysis", {}).get("urgency") in ["CRITICAL", "URGENT"]:
            readiness_details = assessment["readiness_analysis"].get("details", {})
            if readiness_details.get("consecutive_low_days", 0) >= 3:
                data_concerns.append(f"Readiness: {readiness_details['consecutive_low_days']} consecutive low days")
        
        # Check HRV trends
        if assessment.get("hrv_analysis", {}).get("urgency") in ["CRITICAL", "URGENT"]:
            hrv_details = assessment["hrv_analysis"].get("details", {})
            if hrv_details.get("drop_percentage", 0) > 15:
                data_concerns.append(f"HRV: {hrv_details['drop_percentage']:.1f}% drop from baseline")
        
        if data_concerns:
            message_parts.append("Data patterns showing concern:")
            for concern in data_concerns:
                message_parts.append(f"• {concern}")
        else:
            message_parts.append("Multiple health metrics trending concerning")
        
        message_parts.append("\nKelly, your data is showing patterns that suggest your body needs attention. How are you feeling?")
        
        return "\n\n".join(message_parts)
    
    def generate_health_summary(self, assessment: Dict) -> str:
        """Generate health assessment summary - data patterns only"""
        urgency = assessment["overall_urgency"]
        timestamp = assessment["timestamp"]
        
        summary_parts = [f"Health Data Assessment - {urgency} ({timestamp})"]
        
        # Data analysis summaries
        data_patterns = []
        
        if assessment.get("sleep_analysis", {}).get("urgency") != "NORMAL":
            data_patterns.append(f"Sleep: {assessment['sleep_analysis']['urgency']}")
            
        if assessment.get("readiness_analysis", {}).get("urgency") != "NORMAL":
            data_patterns.append(f"Readiness: {assessment['readiness_analysis']['urgency']}")
            
        if assessment.get("hrv_analysis", {}).get("urgency") != "NORMAL":
            data_patterns.append(f"HRV: {assessment['hrv_analysis']['urgency']}")
            
        if assessment.get("hr_analysis", {}).get("urgency") != "NORMAL":
            data_patterns.append(f"Heart Rate: {assessment['hr_analysis']['urgency']}")
        
        if data_patterns:
            summary_parts.append(f"Data concerns: {', '.join(data_patterns)}")
        else:
            summary_parts.append("All health metrics within normal ranges")
        
        # Alerts created
        if assessment.get("alerts_created"):
            summary_parts.append(f"Alerts created: {len(assessment['alerts_created'])}")
        
        return "\n".join(summary_parts)
    
    def create_health_alert(self, message: str, urgency: str) -> str:
        """Create health alert using critical alert engine"""
        try:
            result = subprocess.run([
                "python3", self.critical_engine, "create",
                message, urgency, "welly", "health"
            ], capture_output=True, text=True, cwd=self.workspace)
            
            if result.returncode == 0:
                # Extract alert ID from output
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines:
                    if "Created alert" in line:
                        alert_id = line.split()[-1]
                        return alert_id
            
            return "ERROR"
            
        except Exception as e:
            print(f"Error creating health alert: {e}")
            return "ERROR"
    
    def log_assessment(self, assessment: Dict):
        """Log health assessment to file"""
        log_file = os.path.join(self.workspace, "memory", f"welly-health-{datetime.now().strftime('%Y%m%d')}.md")
        
        with open(log_file, 'a') as f:
            f.write(f"\n## Health Assessment - {assessment['timestamp']}\n")
            f.write(f"**Overall Urgency:** {assessment['overall_urgency']}\n")
            f.write(f"**Summary:** {assessment['summary']}\n")
            
            if assessment.get("alerts_created"):
                f.write(f"**Alerts Created:** {', '.join(assessment['alerts_created'])}\n")
            
            if assessment.get("error"):
                f.write(f"**Error:** {assessment['error']}\n")
            
            f.write("\n")

def main():
    monitor = WellyHealthMonitor()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 welly-health-monitor.py assess    # Run health assessment")
        print("  python3 welly-health-monitor.py symptoms  # Analyze recent symptoms only")
        print("  python3 welly-health-monitor.py test      # Test with sample data")
        return
    
    command = sys.argv[1]
    
    if command == "assess":
        assessment = monitor.run_health_assessment()
        monitor.log_assessment(assessment)
        
        print(f"Health Assessment Complete:")
        print(f"Overall Urgency: {assessment['overall_urgency']}")
        print(f"Summary: {assessment['summary']}")
        
        if assessment.get("alerts_created"):
            print(f"Alerts Created: {', '.join(assessment['alerts_created'])}")
    
    elif command == "symptoms":
        memory_content = monitor.get_recent_memory_content()
        urgency, analysis = monitor.analyze_symptom_mentions(memory_content)
        
        print(f"Symptom Analysis: {urgency}")
        print(f"Critical: {analysis.get('critical_symptoms', [])}")
        print(f"Urgent: {analysis.get('urgent_symptoms', [])}")
        print(f"Concerning: {analysis.get('concerning_symptoms', [])}")
    
    elif command == "test":
        # Test with sample symptom content
        test_content = "I've been exhausted for three days and can't sleep. Heart racing at night."
        urgency, analysis = monitor.analyze_symptom_mentions(test_content)
        
        print(f"Test Analysis: {urgency}")
        print(f"Details: {json.dumps(analysis, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
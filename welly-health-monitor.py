#!/usr/bin/env python3
"""
Welly Health Monitor - Critical Alert Integration

Monitors health patterns from Oura/Strava data and creates critical alerts
for concerning trends that require immediate attention.
"""

import json
import os
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
        """Analyze memory files for health symptom mentions"""
        content_lower = memory_content.lower()
        
        analysis = {
            "critical_symptoms": [],
            "urgent_symptoms": [],
            "concerning_symptoms": [],
            "recent_mentions": []
        }
        
        # Check for symptom keywords
        for symptom in self.symptom_keywords["critical"]:
            if symptom in content_lower:
                analysis["critical_symptoms"].append(symptom)
        
        for symptom in self.symptom_keywords["urgent"]:
            if symptom in content_lower:
                analysis["urgent_symptoms"].append(symptom)
        
        for symptom in self.symptom_keywords["concerning"]:
            if symptom in content_lower:
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
        """Get recent memory content for symptom analysis"""
        memory_dir = os.path.join(self.workspace, "memory")
        content = ""
        
        for i in range(days_back):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = os.path.join(memory_dir, f"{date}.md")
            
            if os.path.exists(memory_file):
                with open(memory_file, 'r') as f:
                    content += f"\n{f.read()}"
        
        return content
    
    def run_health_assessment(self) -> Dict:
        """Run complete health assessment and return findings"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "sleep_analysis": {},
            "readiness_analysis": {},
            "hrv_analysis": {},
            "hr_analysis": {},
            "symptom_analysis": {},
            "overall_urgency": "NORMAL",
            "alerts_created": [],
            "summary": ""
        }
        
        try:
            # For now, simulate health data analysis
            # In real implementation, this would fetch actual Oura/Strava data
            
            # Analyze recent memory for symptoms
            memory_content = self.get_recent_memory_content()
            symptom_urgency, symptom_analysis = self.analyze_symptom_mentions(memory_content)
            assessment["symptom_analysis"] = {
                "urgency": symptom_urgency,
                "details": symptom_analysis
            }
            
            # Simulate other health metrics (replace with real data fetching)
            # This would integrate with actual Oura/Strava APIs
            
            # Determine overall urgency (highest of all analyses)
            urgencies = [symptom_urgency]
            if "CRITICAL" in urgencies:
                assessment["overall_urgency"] = "CRITICAL"
            elif "URGENT" in urgencies:
                assessment["overall_urgency"] = "URGENT"
            
            # Create alerts if needed
            if assessment["overall_urgency"] in ["CRITICAL", "URGENT"]:
                alert_message = self.generate_health_alert_message(assessment)
                alert_id = self.create_health_alert(alert_message, assessment["overall_urgency"])
                assessment["alerts_created"].append(alert_id)
            
            # Generate summary
            assessment["summary"] = self.generate_health_summary(assessment)
            
        except Exception as e:
            assessment["error"] = str(e)
            assessment["summary"] = f"Health assessment failed: {e}"
        
        return assessment
    
    def generate_health_alert_message(self, assessment: Dict) -> str:
        """Generate alert message based on health assessment"""
        urgency = assessment["overall_urgency"]
        
        if urgency == "CRITICAL":
            prefix = "🚨 CRITICAL HEALTH ALERT"
        else:
            prefix = "⚠️ URGENT HEALTH CONCERN"
        
        message_parts = [prefix]
        
        # Add symptom concerns
        symptom_analysis = assessment.get("symptom_analysis", {})
        if symptom_analysis.get("details", {}).get("critical_symptoms"):
            symptoms = ", ".join(symptom_analysis["details"]["critical_symptoms"])
            message_parts.append(f"Critical symptoms mentioned recently: {symptoms}")
        elif symptom_analysis.get("details", {}).get("urgent_symptoms"):
            symptoms = ", ".join(symptom_analysis["details"]["urgent_symptoms"])
            message_parts.append(f"Concerning symptoms mentioned: {symptoms}")
        
        # Add data concerns (when real data is available)
        # if assessment.get("sleep_analysis", {}).get("urgency") in ["CRITICAL", "URGENT"]:
        #     message_parts.append("Sleep patterns showing concerning trends")
        
        message_parts.append("\nKelly, I'm noticing some health patterns that need attention. Can you check in on how you're feeling?")
        
        return "\n\n".join(message_parts)
    
    def generate_health_summary(self, assessment: Dict) -> str:
        """Generate health assessment summary"""
        urgency = assessment["overall_urgency"]
        timestamp = assessment["timestamp"]
        
        summary_parts = [f"Health Assessment - {urgency} ({timestamp})"]
        
        # Symptom analysis
        symptom_analysis = assessment.get("symptom_analysis", {})
        if symptom_analysis.get("urgency") != "NORMAL":
            symptom_details = symptom_analysis.get("details", {})
            summary_parts.append(f"Symptom concerns: {symptom_analysis['urgency']}")
            
            if symptom_details.get("critical_symptoms"):
                summary_parts.append(f"  Critical: {', '.join(symptom_details['critical_symptoms'])}")
            if symptom_details.get("urgent_symptoms"):
                summary_parts.append(f"  Urgent: {', '.join(symptom_details['urgent_symptoms'])}")
        
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
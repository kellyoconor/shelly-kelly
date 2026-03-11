#!/usr/bin/env python3
"""
Netty Urgent Pattern Adapter

Integrates Netty gap detection with critical alert safeguard system.
Classifies gap findings for urgency and routes them appropriately.
"""

import json
import os
import re
import sys
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

class NettyUrgentAdapter:
    def __init__(self):
        self.workspace = "/data/workspace"
        self.pending_checkins_file = os.path.join(self.workspace, "pending_checkins.md")
        self.critical_engine = os.path.join(self.workspace, "critical-alert-engine.py")
        
        # Urgency patterns for gap detection
        self.urgency_patterns = {
            "CRITICAL": {
                "time_indicators": [
                    r"tomorrow", r"today", r"in \d+ hours?", r"flight.*\d+:\d+",
                    r"departure.*\d+:\d+", r"boarding", r"gate", r"airport",
                    r"leaving in", r"check[- ]out", r"medication.*missed",
                    r"doctor.*urgent", r"emergency", r"pain.*severe"
                ],
                "health_patterns": [
                    r"readiness.*[<].*50", r"sleep.*[<].*5.*hours?",
                    r"hrv.*drop.*\d+%", r"heart rate.*elevated",
                    r"multiple.*nights?.*awake", r"can't sleep.*days?"
                ],
                "travel_critical": [
                    r"flight.*tomorrow", r"departure.*hours?",
                    r"boarding pass", r"confirmation.*needed",
                    r"hotel.*tonight", r"reservation.*expires?"
                ]
            },
            "URGENT": {
                "time_indicators": [
                    r"this week", r"deadline", r"interview.*\d+ days? ago",
                    r"appointment.*yesterday", r"results.*waiting",
                    r"booking.*expires?", r"reservation.*pending"
                ],
                "health_patterns": [
                    r"readiness.*[<].*60.*\d+ days?",
                    r"recovery.*concerning", r"pattern.*unusual",
                    r"energy.*low.*days?", r"tired.*consistently"
                ],
                "social_urgent": [
                    r"family.*emergency", r"friend.*crisis",
                    r"job.*deadline", r"application.*due"
                ]
            }
        }
        
        # Keywords that indicate high importance regardless of timing
        self.importance_keywords = [
            "health", "medical", "doctor", "hospital", "pain", "sick",
            "flight", "travel", "airport", "hotel", "reservation",
            "interview", "job", "deadline", "application", "urgent",
            "emergency", "family", "mom", "dad"
        ]
    
    def analyze_gap_urgency(self, gap_content: str, gap_context: Dict = None) -> Tuple[str, Dict]:
        """Analyze a gap for urgency level and reasoning"""
        content_lower = gap_content.lower()
        
        urgency_reasons = {
            "CRITICAL": [],
            "URGENT": [],
            "importance_score": 0
        }
        
        # Check critical patterns
        for category, patterns in self.urgency_patterns["CRITICAL"].items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    urgency_reasons["CRITICAL"].append(f"{category}: {pattern}")
        
        # Check urgent patterns
        for category, patterns in self.urgency_patterns["URGENT"].items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    urgency_reasons["URGENT"].append(f"{category}: {pattern}")
        
        # Calculate importance score
        for keyword in self.importance_keywords:
            if keyword in content_lower:
                urgency_reasons["importance_score"] += 1
        
        # Apply context-based scoring
        if gap_context:
            days_old = gap_context.get("days_old", 0)
            
            # Time sensitivity scoring
            if days_old <= 1:
                urgency_reasons["importance_score"] += 2  # Very recent
            elif days_old >= 5:
                urgency_reasons["importance_score"] += 1  # Getting stale
        
        # Determine final urgency level
        if urgency_reasons["CRITICAL"]:
            urgency = "CRITICAL"
        elif urgency_reasons["URGENT"] or urgency_reasons["importance_score"] >= 3:
            urgency = "URGENT"
        else:
            urgency = "NORMAL"
        
        return urgency, urgency_reasons
    
    def parse_pending_checkins(self) -> List[Dict]:
        """Parse pending_checkins.md for gap prompts"""
        if not os.path.exists(self.pending_checkins_file):
            return []
        
        with open(self.pending_checkins_file, 'r') as f:
            content = f.read()
        
        gaps = []
        current_gap = None
        
        # Parse markdown structure for gap prompts
        lines = content.split('\n')
        for line in lines:
            # Look for gap headers (### patterns)
            if line.startswith('### '):
                if current_gap:
                    gaps.append(current_gap)
                
                # Extract priority and title
                header = line[4:].strip()
                priority = "NORMAL"
                
                if "HIGH PRIORITY" in header or "CRITICAL" in header:
                    priority = "CRITICAL"
                elif "URGENT" in header or "⚠️" in header:
                    priority = "URGENT"
                
                current_gap = {
                    "title": header,
                    "priority": priority,
                    "content": "",
                    "category": self.extract_category(header)
                }
            
            # Look for quoted gap prompts
            elif line.startswith('"') and current_gap:
                # Extract the actual prompt content
                prompt = line.strip().strip('"')
                current_gap["content"] = prompt
        
        # Add final gap
        if current_gap:
            gaps.append(current_gap)
        
        return gaps
    
    def extract_category(self, title: str) -> str:
        """Extract category from gap title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["travel", "flight", "airport", "hotel"]):
            return "travel"
        elif any(word in title_lower for word in ["wellness", "health", "medical"]):
            return "wellness"
        elif any(word in title_lower for word in ["family", "mom", "dad", "friend"]):
            return "social"
        elif any(word in title_lower for word in ["work", "interview", "job", "deadline"]):
            return "work"
        else:
            return "general"
    
    def process_gaps_for_urgency(self) -> Dict:
        """Process all gaps and classify them for critical alert routing"""
        gaps = self.parse_pending_checkins()
        
        processing_results = {
            "total_gaps": len(gaps),
            "critical_alerts_created": 0,
            "urgent_alerts_created": 0,
            "normal_gaps_kept": 0,
            "processed_gaps": []
        }
        
        for gap in gaps:
            # Analyze gap urgency
            detected_urgency, reasons = self.analyze_gap_urgency(gap["content"])
            
            # Use explicit priority if set, otherwise use detected
            final_urgency = gap.get("priority", detected_urgency)
            if detected_urgency == "CRITICAL" and final_urgency != "CRITICAL":
                final_urgency = "CRITICAL"  # Always escalate detected critical
            
            gap_result = {
                "title": gap["title"],
                "content": gap["content"],
                "category": gap["category"],
                "netty_priority": gap.get("priority", "NORMAL"),
                "detected_urgency": detected_urgency,
                "final_urgency": final_urgency,
                "urgency_reasons": reasons
            }
            
            # Route based on urgency
            if final_urgency in ["CRITICAL", "URGENT"]:
                # Create critical alert
                alert_id = self.create_critical_alert(gap, final_urgency)
                gap_result["alert_id"] = alert_id
                
                if final_urgency == "CRITICAL":
                    processing_results["critical_alerts_created"] += 1
                else:
                    processing_results["urgent_alerts_created"] += 1
            else:
                # Keep as normal gap for heartbeat system
                processing_results["normal_gaps_kept"] += 1
            
            processing_results["processed_gaps"].append(gap_result)
        
        return processing_results
    
    def create_critical_alert(self, gap: Dict, urgency: str) -> str:
        """Create critical alert from gap"""
        try:
            result = subprocess.run([
                "python3", self.critical_engine, "create",
                gap["content"], urgency, "netty", gap["category"]
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
            print(f"Error creating critical alert: {e}")
            return "ERROR"
    
    def update_pending_checkins(self, processing_results: Dict):
        """Update pending_checkins.md to remove promoted urgent items"""
        if processing_results["critical_alerts_created"] == 0 and processing_results["urgent_alerts_created"] == 0:
            return  # Nothing to update
        
        # Read current content
        with open(self.pending_checkins_file, 'r') as f:
            content = f.read()
        
        # Build new content with normal gaps only
        normal_gaps = [g for g in processing_results["processed_gaps"] 
                      if g["final_urgency"] == "NORMAL"]
        
        if not normal_gaps:
            # No normal gaps left - clear file but leave header
            new_content = "# Pending Check-ins for Shelly\n\n*No normal gaps detected - urgent items promoted to critical alert system*\n"
        else:
            # Rebuild with normal gaps
            new_content = "# Pending Check-ins for Shelly\n\n"
            new_content += f"## From Netty's Gap Detection ({datetime.now().strftime('%B %d, %Y')})\n\n"
            
            for gap in normal_gaps:
                new_content += f"### {gap['title']}\n"
                new_content += f'"{gap["content"]}"\n\n'
            
            new_content += "---\n"
            new_content += f"*Generated by Netty's enhanced pattern recognition*\n"
            new_content += f"*{processing_results['critical_alerts_created']} critical and {processing_results['urgent_alerts_created']} urgent items promoted to alert system*\n"
        
        # Write updated content
        with open(self.pending_checkins_file, 'w') as f:
            f.write(new_content)
    
    def generate_summary_report(self, processing_results: Dict) -> str:
        """Generate summary of urgency processing"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = []
        report.append(f"# Netty Urgency Processing Report - {timestamp}")
        report.append("")
        report.append("## Summary")
        report.append(f"- Total gaps processed: {processing_results['total_gaps']}")
        report.append(f"- Critical alerts created: {processing_results['critical_alerts_created']}")
        report.append(f"- Urgent alerts created: {processing_results['urgent_alerts_created']}")
        report.append(f"- Normal gaps kept: {processing_results['normal_gaps_kept']}")
        report.append("")
        
        if processing_results["critical_alerts_created"] > 0 or processing_results["urgent_alerts_created"] > 0:
            report.append("## 🚨 Promoted to Critical Alert System")
            for gap in processing_results["processed_gaps"]:
                if gap["final_urgency"] in ["CRITICAL", "URGENT"]:
                    report.append(f"### {gap['final_urgency']}: {gap['title']}")
                    report.append(f"**Content:** {gap['content']}")
                    report.append(f"**Category:** {gap['category']}")
                    report.append(f"**Alert ID:** {gap.get('alert_id', 'ERROR')}")
                    
                    if gap["urgency_reasons"]["CRITICAL"]:
                        report.append(f"**Critical patterns:** {', '.join(gap['urgency_reasons']['CRITICAL'])}")
                    if gap["urgency_reasons"]["URGENT"]:
                        report.append(f"**Urgent patterns:** {', '.join(gap['urgency_reasons']['URGENT'])}")
                    
                    report.append("")
        
        if processing_results["normal_gaps_kept"] > 0:
            report.append("## Normal Gaps (Kept for Heartbeat)")
            for gap in processing_results["processed_gaps"]:
                if gap["final_urgency"] == "NORMAL":
                    report.append(f"- {gap['title'][:60]}...")
            report.append("")
        
        return "\n".join(report)
    
    def run_full_processing(self) -> str:
        """Run complete urgency processing pipeline"""
        print("Starting Netty urgency processing...")
        
        # Process gaps for urgency
        results = self.process_gaps_for_urgency()
        
        if results["total_gaps"] == 0:
            return "No gaps found to process."
        
        # Update pending checkins file
        self.update_pending_checkins(results)
        
        # Generate and save report
        report = self.generate_summary_report(results)
        
        # Save to log
        log_file = os.path.join(self.workspace, "memory", f"netty-urgency-{datetime.now().strftime('%Y%m%d')}.md")
        with open(log_file, 'a') as f:
            f.write(f"\n{report}\n")
        
        # Print summary
        summary = f"Processed {results['total_gaps']} gaps: {results['critical_alerts_created']} critical, {results['urgent_alerts_created']} urgent, {results['normal_gaps_kept']} normal"
        print(summary)
        
        return summary

def main():
    adapter = NettyUrgentAdapter()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 netty-urgent-adapter.py process    # Process current gaps for urgency")
        print("  python3 netty-urgent-adapter.py analyze    # Analyze gaps without routing")
        print("  python3 netty-urgent-adapter.py test <text> # Test urgency classification")
        return
    
    command = sys.argv[1]
    
    if command == "process":
        result = adapter.run_full_processing()
        print(result)
    
    elif command == "analyze":
        gaps = adapter.parse_pending_checkins()
        
        if not gaps:
            print("No gaps found in pending_checkins.md")
            return
        
        print(f"Found {len(gaps)} gaps to analyze:")
        print()
        
        for gap in gaps:
            urgency, reasons = adapter.analyze_gap_urgency(gap["content"])
            print(f"Gap: {gap['title']}")
            print(f"Content: {gap['content'][:80]}...")
            print(f"Category: {gap['category']}")
            print(f"Detected urgency: {urgency}")
            print(f"Reasons: {json.dumps(reasons, indent=2)}")
            print("-" * 60)
    
    elif command == "test":
        if len(sys.argv) < 3:
            print("Error: Test text required")
            return
        
        test_text = sys.argv[2]
        urgency, reasons = adapter.analyze_gap_urgency(test_text)
        
        print(f"Test text: {test_text}")
        print(f"Detected urgency: {urgency}")
        print(f"Analysis: {json.dumps(reasons, indent=2)}")
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
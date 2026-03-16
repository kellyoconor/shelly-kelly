#!/usr/bin/env python3
"""
Alert Cleanup Script

Removes old resolved alerts to keep the system clean.
Keeps recent alerts for debugging, removes older ones.
"""

import json
import os
from datetime import datetime, timedelta

def cleanup_alerts(keep_days=7):
    """Clean up alerts older than keep_days"""
    workspace = "/data/workspace"
    alerts_file = os.path.join(workspace, "critical-alerts.json")
    
    if not os.path.exists(alerts_file):
        print("No alerts file found")
        return {"cleaned": 0, "kept": 0}
    
    # Load current alerts
    with open(alerts_file, 'r') as f:
        alerts = json.load(f)
    
    # Calculate cutoff date
    cutoff = datetime.now() - timedelta(days=keep_days)
    
    # Filter alerts
    kept_alerts = []
    cleaned_count = 0
    
    for alert in alerts:
        try:
            alert_time = datetime.fromisoformat(alert.get('timestamp', ''))
            
            # Keep if:
            # 1. Recent (within keep_days) AND not a test/resolved alert
            # 2. Still active (not resolved)
            # 3. Has unresolved delivery failures that are recent
            status = alert.get('status', '')
            is_resolved_test = status in ['RESOLVED_TEST', 'FALSE_ALERT', 'RESOLVED_MANUAL', 'RESOLVED_SUBSTRING_BUG']
            
            should_keep = (
                # Keep recent non-test alerts
                (alert_time > cutoff and not is_resolved_test) or
                # Keep any truly active alerts
                status.startswith('ACTIVE') or
                # Keep recent unresolved delivery failures
                (alert_time > cutoff and
                 alert.get('delivery_attempts', []) and 
                 not any(attempt.get('success', False) for attempt in alert.get('delivery_attempts', [])) and
                 not alert.get('resolved', False))
            )
            
            if should_keep:
                kept_alerts.append(alert)
            else:
                cleaned_count += 1
                
        except (ValueError, KeyError) as e:
            # Keep malformed alerts for safety
            print(f"Warning: malformed alert kept: {e}")
            kept_alerts.append(alert)
    
    # Write back cleaned alerts
    with open(alerts_file, 'w') as f:
        json.dump(kept_alerts, f, indent=2)
    
    print(f"Cleaned {cleaned_count} old alerts, kept {len(kept_alerts)}")
    return {"cleaned": cleaned_count, "kept": len(kept_alerts)}

if __name__ == "__main__":
    import sys
    
    # Allow custom keep_days from command line
    keep_days = 7
    if len(sys.argv) > 1:
        try:
            keep_days = int(sys.argv[1])
        except ValueError:
            print(f"Invalid days value: {sys.argv[1]}, using default 7")
    
    result = cleanup_alerts(keep_days)
    print(f"Cleanup complete: {result}")
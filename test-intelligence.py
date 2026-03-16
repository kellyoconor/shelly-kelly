#!/usr/bin/env python3
"""
Test the intelligence algorithms with sample data
"""

import tempfile
import os
import sys
sys.path.append('/data/workspace/scripts')
from intelligence_builder import KellyIntelligence

# Create test daily note with health and decision data
test_content = """# March 15, 2026

## Health
- Readiness: 85%
- Sleep: 7.2h
- HRV: 42
- Energy: high

## Events
- Decided to run 6 miles this morning
- Chose to skip the evening meeting
- Going to focus on the architecture project

## Thoughts
- Feeling energized after good sleep
- Clear thinking today
"""

# Create temporary test file
with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
    f.write(test_content)
    test_file = f.name

# Test parsing
intel = KellyIntelligence()

print("🧪 Testing health data extraction:")
with open(test_file, 'r') as f:
    content = f.read()

from datetime import datetime
health_data = intel._extract_health_data(content, datetime.now())
print(f"Health data: {health_data}")

decisions = intel._extract_decisions(content, datetime.now())
print(f"Decisions: {decisions}")

# Cleanup
os.unlink(test_file)
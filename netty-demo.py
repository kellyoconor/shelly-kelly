#!/usr/bin/env python3
"""
Netty Demo - Show what patterns Netty can detect
"""

import sys
sys.path.insert(0, '/data/workspace')

from netty import NettyScanner
from pathlib import Path

def demo_netty():
    print("🔍 Netty Gap Detector Demo")
    print("=" * 40)
    
    scanner = NettyScanner()
    
    # Show what files Netty scans
    memory_files = list(scanner.memory_dir.glob("2026-*.md"))
    recent_files = sorted(memory_files, key=lambda f: f.stat().st_mtime, reverse=True)[:3]
    
    print(f"\n📁 Memory Files Scanned (last 3):")
    for file in recent_files:
        print(f"  • {file.name}")
    
    # Show pattern detection capabilities
    print(f"\n🔍 Pattern Detection Categories:")
    print(f"  👥 People: {', '.join(scanner.people_keywords['family'] + scanner.people_keywords['friends'][:3])}")
    print(f"  📅 Events: {', '.join(scanner.event_keywords[:5])}")  
    print(f"  😰 Stress: {', '.join(scanner.stress_keywords[:5])}")
    
    # Run scan and show results
    print(f"\n🚀 Running Gap Detection Scan...")
    results = scanner.run_scan("light")
    
    print(f"\n📊 Results:")
    print(f"  • Gaps found: {results['gaps_found']}")
    print(f"  • Check-in prompts generated: {results['prompts_generated']}")
    
    # Show sample outputs
    output_file = Path("/data/workspace/pending_checkins.md")
    if output_file.exists():
        content = output_file.read_text()
        prompts = []
        for line in content.split('\n'):
            if line.startswith('**') and '.**' in line:
                prompt = line.split('**')[2].strip()
                if prompt and len(prompt) > 10:
                    prompts.append(prompt)
        
        if prompts:
            print(f"\n💬 Sample Check-in Prompts Generated:")
            for i, prompt in enumerate(prompts[:2], 1):
                print(f"  {i}. {prompt}")
            if len(prompts) > 2:
                print(f"  ... and {len(prompts) - 2} more")
    
    print(f"\n✅ Demo Complete!")
    print(f"\n📄 Output files:")
    print(f"  • pending_checkins.md - For Shelly to read during heartbeats")
    print(f"  • netty_log.md - Scan history and reasoning")

if __name__ == "__main__":
    demo_netty()
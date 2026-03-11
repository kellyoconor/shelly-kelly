#!/usr/bin/env python3
"""
Test script for Netty system
"""

import sys
import os
from pathlib import Path

# Add current directory to path for importing netty
sys.path.insert(0, '/data/workspace')

from netty import NettyScanner

def test_netty_basic():
    """Test basic Netty functionality"""
    print("🧪 Testing Netty Gap Detector...")
    
    scanner = NettyScanner()
    
    # Test file paths
    print("📁 Checking file paths:")
    print(f"  Workspace: {scanner.workspace} - {'✅' if scanner.workspace.exists() else '❌'}")
    print(f"  Kelly vault: {scanner.kelly_vault} - {'✅' if scanner.kelly_vault.exists() else '❌'}")
    print(f"  Memory dir: {scanner.memory_dir} - {'✅' if scanner.memory_dir.exists() else '❌'}")
    
    # Check memory files
    memory_files = list(scanner.memory_dir.glob("2026-*.md"))
    print(f"  Memory files found: {len(memory_files)}")
    
    # Test a light scan
    print("\n🔍 Running test scan...")
    results = scanner.run_scan("light")
    
    print(f"\n📊 Scan Results:")
    print(f"  Gaps found: {results['gaps_found']}")
    print(f"  Prompts generated: {results['prompts_generated']}")
    
    if results['top_gaps']:
        print(f"  Top gaps:")
        for gap in results['top_gaps']:
            print(f"    - {gap}")
    
    # Check output files
    print(f"\n📄 Output Files:")
    output_file = Path("/data/workspace/pending_checkins.md")
    log_file = Path("/data/kelly-vault/netty_log.md")
    
    print(f"  pending_checkins.md: {'✅' if output_file.exists() else '❌'}")
    print(f"  netty_log.md: {'✅' if log_file.exists() else '❌'}")
    
    # Show sample output
    if output_file.exists():
        print(f"\n💬 Sample Check-in Prompts:")
        content = output_file.read_text()
        lines = content.split('\n')
        for line in lines:
            if line.startswith('**') and line.endswith('**'):
                continue
            if line.strip() and not line.startswith('#') and not line.startswith('*'):
                print(f"    {line.strip()}")
    
    print(f"\n✅ Netty test complete!")

if __name__ == "__main__":
    test_netty_basic()
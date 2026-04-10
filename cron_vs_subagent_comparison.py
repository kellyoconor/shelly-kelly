#!/usr/bin/env python3
"""
Compare cron-like execution vs subagent execution for morning briefing.
Simulates what would happen in a real cron environment.
"""

import os
import sys
import time
import json
import subprocess
import socket
from datetime import datetime

def log_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def simulate_cron_environment():
    """Simulate the restricted environment a cron job runs in"""
    log_section("SIMULATING CRON ENVIRONMENT")
    
    # Save original environment
    original_env = dict(os.environ)
    
    # Minimal cron environment (what cron typically provides)
    cron_env = {
        'PATH': '/usr/bin:/bin',  # Much more restricted PATH
        'HOME': '/root',
        'LOGNAME': 'root',
        'SHELL': '/bin/sh',
        'USER': 'root',
        'LANG': 'C',
        'LC_ALL': 'C'
    }
    
    print("Original environment variables (key ones):")
    for key in ['PATH', 'PYTHONPATH', 'PWD', 'OLDPWD']:
        print(f"  {key}: {original_env.get(key, '[NOT SET]')}")
    
    print(f"\nTotal original env vars: {len(original_env)}")
    
    print("\nSimulated cron environment:")
    for key, value in cron_env.items():
        print(f"  {key}: {value}")
    
    print(f"\nTotal cron env vars: {len(cron_env)}")
    
    return original_env, cron_env

def run_in_environment(cmd, env_dict, description):
    """Run a command in a specific environment"""
    print(f"\n--- {description} ---")
    print(f"Command: {cmd}")
    print(f"Environment variables: {len(env_dict)}")
    
    start_time = time.time()
    
    try:
        # Run with specific environment
        result = subprocess.run(
            cmd,
            shell=True,
            env=env_dict,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/data/workspace"  # Force working directory
        )
        
        execution_time = time.time() - start_time
        
        print(f"Exit code: {result.returncode}")
        print(f"Execution time: {execution_time:.3f}s")
        
        if result.stdout:
            stdout = result.stdout.strip()
            print(f"STDOUT ({len(stdout)} chars):")
            print(stdout[:500] + ("..." if len(stdout) > 500 else ""))
        
        if result.stderr:
            stderr = result.stderr.strip()
            print(f"STDERR ({len(stderr)} chars):")
            print(stderr[:500] + ("..." if len(stderr) > 500 else ""))
        
        return {
            'success': result.returncode == 0,
            'exit_code': result.returncode,
            'time': execution_time,
            'stdout_len': len(result.stdout) if result.stdout else 0,
            'stderr_len': len(result.stderr) if result.stderr else 0
        }
        
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"❌ TIMEOUT after {execution_time:.3f}s")
        return {
            'success': False,
            'exit_code': 'TIMEOUT',
            'time': execution_time,
            'stdout_len': 0,
            'stderr_len': 0
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ ERROR: {e}")
        return {
            'success': False,
            'exit_code': f'ERROR: {e}',
            'time': execution_time,
            'stdout_len': 0,
            'stderr_len': 0
        }

def test_morning_briefing_commands():
    """Test the actual commands that would be run in morning briefing"""
    log_section("MORNING BRIEFING COMMAND TESTS")
    
    # Get environments
    original_env, cron_env = simulate_cron_environment()
    
    # Define the commands to test
    commands = [
        # Weather (using curl as per SKILL.md)
        ('weather', 'curl -s "wttr.in/Philadelphia?format=%l:+%c+%t+%h+%w"'),
        
        # Oura (requires python3 and working directory)
        ('oura', 'python3 /data/workspace/skills/oura/scripts/oura.py brief'),
        
        # Mirror (requires python3 and working directory) 
        ('mirror', 'python3 /data/workspace/skills/mirror/scripts/mirror.py'),
        
        # Basic Python test
        ('python_test', 'python3 -c "import sys; print(f\\"Python OK: {sys.version}\\")"'),
        
        # Path test
        ('path_test', 'which python3'),
        
        # Working directory test
        ('pwd_test', 'pwd && ls -la | head -5'),
    ]
    
    results = {}
    
    for name, cmd in commands:
        log_section(f"TESTING COMMAND: {name}")
        
        # Test in subagent environment (current/full environment)
        subagent_result = run_in_environment(cmd, original_env, f"{name} - SUBAGENT environment")
        
        # Test in cron-like environment
        cron_result = run_in_environment(cmd, cron_env, f"{name} - CRON environment")
        
        results[name] = {
            'subagent': subagent_result,
            'cron': cron_result,
            'difference': {
                'success_diff': subagent_result['success'] != cron_result['success'],
                'time_diff': abs(subagent_result['time'] - cron_result['time']),
                'exit_code_diff': subagent_result['exit_code'] != cron_result['exit_code']
            }
        }
    
    return results

def analyze_differences(results):
    """Analyze the key differences between cron and subagent execution"""
    log_section("DIFFERENCE ANALYSIS")
    
    print("COMMAND COMPARISON SUMMARY:")
    print("-" * 80)
    print(f"{'Command':<15} {'Subagent':<12} {'Cron':<12} {'Time Diff':<10} {'Issue'}")
    print("-" * 80)
    
    critical_differences = []
    
    for name, data in results.items():
        sub_status = "✅ OK" if data['subagent']['success'] else "❌ FAIL"
        cron_status = "✅ OK" if data['cron']['success'] else "❌ FAIL"
        time_diff = data['difference']['time_diff']
        
        issue = ""
        if data['difference']['success_diff']:
            if data['subagent']['success'] and not data['cron']['success']:
                issue = "CRON FAILS"
                critical_differences.append({
                    'command': name,
                    'issue': 'Cron execution failed',
                    'subagent_exit': data['subagent']['exit_code'],
                    'cron_exit': data['cron']['exit_code']
                })
            elif not data['subagent']['success'] and data['cron']['success']:
                issue = "SUBAGENT FAILS"
        elif time_diff > 1.0:
            issue = "SLOW"
        else:
            issue = "OK"
        
        print(f"{name:<15} {sub_status:<12} {cron_status:<12} {time_diff:<10.3f} {issue}")
    
    print("\nCRITICAL DIFFERENCES FOUND:")
    if critical_differences:
        for diff in critical_differences:
            print(f"\n❌ {diff['command'].upper()}:")
            print(f"   Issue: {diff['issue']}")
            print(f"   Subagent exit code: {diff['subagent_exit']}")
            print(f"   Cron exit code: {diff['cron_exit']}")
    else:
        print("✅ No critical execution differences found")
    
    return critical_differences

def check_file_permissions():
    """Check if file permissions could be causing cron issues"""
    log_section("FILE PERMISSION ANALYSIS")
    
    critical_files = [
        '/data/workspace/skills/oura/scripts/oura.py',
        '/data/workspace/skills/mirror/scripts/mirror.py',
        '/data/workspace/skills/oura/scripts/__pycache__',
        '/data/workspace/skills/mirror/scripts/__pycache__',
        '/tmp',
        '/data/workspace',
        '/data/kelly-vault'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            try:
                stat_info = os.stat(file_path)
                permissions = oct(stat_info.st_mode)[-3:]
                readable = os.access(file_path, os.R_OK)
                writable = os.access(file_path, os.W_OK)
                executable = os.access(file_path, os.X_OK)
                
                print(f"{file_path}:")
                print(f"  Permissions: {permissions}")
                print(f"  Access: R={readable} W={writable} X={executable}")
                print(f"  Owner: UID={stat_info.st_uid} GID={stat_info.st_gid}")
                
            except Exception as e:
                print(f"{file_path}: Error checking - {e}")
        else:
            print(f"{file_path}: NOT FOUND")
        print()

def main():
    print(f"🔍 CRON vs SUBAGENT COMPARISON - {datetime.now().isoformat()}")
    print("=" * 60)
    
    # Step 1: Environment comparison and command testing
    results = test_morning_briefing_commands()
    
    # Step 2: Analyze critical differences  
    differences = analyze_differences(results)
    
    # Step 3: Check file permissions
    check_file_permissions()
    
    # Step 4: Save comprehensive results
    comparison_data = {
        'timestamp': datetime.now().isoformat(),
        'test_type': 'cron_vs_subagent_comparison',
        'results': results,
        'critical_differences': differences,
        'environment_info': {
            'current_uid': os.getuid(),
            'current_gid': os.getgid(),
            'working_directory': os.getcwd(),
            'python_executable': sys.executable,
            'python_version': sys.version
        }
    }
    
    result_file = '/data/workspace/cron_vs_subagent_analysis.json'
    with open(result_file, 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"\n📊 Detailed analysis saved to: {result_file}")
    
    # Final summary
    log_section("KEY FINDINGS")
    
    if differences:
        print("🚨 CRITICAL DIFFERENCES IDENTIFIED:")
        for diff in differences:
            print(f"  • {diff['command']}: {diff['issue']}")
        print("\nThese differences explain why morning briefing fails in cron but works as subagent.")
    else:
        print("✅ No critical differences found between cron and subagent execution.")
        print("The issue may be elsewhere (timing, external dependencies, etc.)")
    
    return len(differences) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
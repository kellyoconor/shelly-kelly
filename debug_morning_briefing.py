#!/usr/bin/env python3
"""
Systematic debug of morning briefing execution.
Logs all environmental details to identify cron vs subagent differences.
"""

import os
import sys
import time
import json
import subprocess
import socket
from datetime import datetime
from pathlib import Path

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

def log_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def log_subsection(title):
    print(f"\n--- {title} ---")

def safe_run_command(cmd, description, timeout=30):
    """Run a command safely with timeout and detailed logging"""
    start_time = time.time()
    log_subsection(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"Start time: {datetime.now().isoformat()}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd="/data/workspace"
        )
        
        execution_time = time.time() - start_time
        print(f"Exit code: {result.returncode}")
        print(f"Execution time: {execution_time:.3f} seconds")
        
        if result.stdout:
            print(f"STDOUT ({len(result.stdout)} chars):")
            print(result.stdout[:1000] + ("..." if len(result.stdout) > 1000 else ""))
        
        if result.stderr:
            print(f"STDERR ({len(result.stderr)} chars):")
            print(result.stderr[:1000] + ("..." if len(result.stderr) > 1000 else ""))
            
        return result, execution_time
    
    except subprocess.TimeoutExpired:
        execution_time = time.time() - start_time
        print(f"❌ TIMEOUT after {execution_time:.3f} seconds")
        return None, execution_time
    
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ ERROR: {e}")
        return None, execution_time

def log_environment():
    """Log all environment details"""
    log_section("ENVIRONMENT ANALYSIS")
    
    # 1. Environment Variables
    log_subsection("1. Environment Variables")
    print("Key environment variables:")
    env_vars = [
        'PATH', 'PYTHONPATH', 'HOME', 'USER', 'SHELL', 'PWD', 'OLDPWD',
        'OPENCLAW_API_KEY', 'OURA_TOKEN', 'GOOGLE_CLIENT_ID', 'SPOTIFY_CLIENT_ID'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, '[NOT SET]')
        if 'TOKEN' in var or 'KEY' in var or 'SECRET' in var:
            if value != '[NOT SET]':
                value = f"[SET - {len(value)} chars]"
        print(f"  {var}: {value}")
    
    print(f"\nTotal environment variables: {len(os.environ)}")
    
    # 2. Working Directory
    log_subsection("2. Working Directory")
    cwd = os.getcwd()
    print(f"Current working directory: {cwd}")
    print(f"Directory exists: {os.path.exists(cwd)}")
    print(f"Directory writable: {os.access(cwd, os.W_OK)}")
    print(f"Directory contents (first 10):")
    try:
        contents = sorted(os.listdir(cwd))[:10]
        for item in contents:
            path = os.path.join(cwd, item)
            size = os.path.getsize(path) if os.path.isfile(path) else "[DIR]"
            print(f"  {item} -> {size}")
    except Exception as e:
        print(f"  Error listing directory: {e}")
    
    # 3. Process Limits
    log_subsection("3. Process Limits") 
    try:
        import resource
        limits = [
            ('RLIMIT_CPU', resource.RLIMIT_CPU),
            ('RLIMIT_FSIZE', resource.RLIMIT_FSIZE),
            ('RLIMIT_DATA', resource.RLIMIT_DATA),
            ('RLIMIT_STACK', resource.RLIMIT_STACK),
            ('RLIMIT_CORE', resource.RLIMIT_CORE),
            ('RLIMIT_RSS', resource.RLIMIT_RSS),
            ('RLIMIT_NPROC', resource.RLIMIT_NPROC),
            ('RLIMIT_NOFILE', resource.RLIMIT_NOFILE),
            ('RLIMIT_MEMLOCK', resource.RLIMIT_MEMLOCK),
            ('RLIMIT_AS', resource.RLIMIT_AS)
        ]
        
        for name, limit_type in limits:
            try:
                soft, hard = resource.getrlimit(limit_type)
                print(f"  {name}: soft={soft}, hard={hard}")
            except:
                print(f"  {name}: [unavailable]")
    except ImportError:
        print("  Resource module not available")
    
    # 4. Memory Usage
    log_subsection("4. Memory Usage")
    if HAS_PSUTIL:
        try:
            memory = psutil.virtual_memory()
            print(f"  Total memory: {memory.total / 1024**3:.2f} GB")
            print(f"  Available memory: {memory.available / 1024**3:.2f} GB")
            print(f"  Memory percent used: {memory.percent:.1f}%")
            print(f"  Free memory: {memory.free / 1024**3:.2f} GB")
            
            # Current process memory
            process = psutil.Process()
            proc_memory = process.memory_info()
            print(f"  Process RSS: {proc_memory.rss / 1024**2:.2f} MB")
            print(f"  Process VMS: {proc_memory.vms / 1024**2:.2f} MB")
        except Exception as e:
            print(f"  Error getting memory info: {e}")
    else:
        print("  psutil not available - using /proc/meminfo")
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
                for line in meminfo.split('\n')[:10]:
                    if line.strip():
                        print(f"  {line}")
        except Exception as e:
            print(f"  Error reading /proc/meminfo: {e}")
    
    # 5. Network Connectivity
    log_subsection("5. Network Connectivity")
    
    # Test basic connectivity
    test_hosts = [
        ('Google DNS', '8.8.8.8', 53),
        ('OpenAI', 'api.openai.com', 443),
        ('Oura API', 'api.ouraring.com', 443),
        ('Google APIs', 'www.googleapis.com', 443)
    ]
    
    for name, host, port in test_hosts:
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            print(f"  ✅ {name} ({host}:{port}): Connected")
        except Exception as e:
            print(f"  ❌ {name} ({host}:{port}): {e}")
    
    # 6. File Permissions
    log_subsection("6. File Permissions")
    
    critical_paths = [
        '/data/workspace',
        '/data/workspace/skills',
        '/data/workspace/skills/weather',
        '/data/workspace/skills/oura', 
        '/data/workspace/skills/mirror',
        '/data/kelly-vault'
    ]
    
    for path in critical_paths:
        if os.path.exists(path):
            stat_info = os.stat(path)
            permissions = oct(stat_info.st_mode)[-3:]
            print(f"  {path}: {permissions} (exists)")
        else:
            print(f"  {path}: [MISSING]")
            
    print(f"\nProcess UID: {os.getuid()}")
    print(f"Process GID: {os.getgid()}")

def test_morning_briefing_components():
    """Test each component of the morning briefing"""
    log_section("MORNING BRIEFING COMPONENTS TEST")
    
    results = {}
    
    # 1. Weather
    log_subsection("TESTING: Weather")
    weather_result, weather_time = safe_run_command(
        "python3 /data/workspace/skills/weather/scripts/weather.py",
        "Weather check"
    )
    results['weather'] = {
        'success': weather_result and weather_result.returncode == 0,
        'time': weather_time,
        'exit_code': weather_result.returncode if weather_result else None
    }
    
    # 2. Oura  
    log_subsection("TESTING: Oura")
    oura_result, oura_time = safe_run_command(
        "python3 /data/workspace/skills/oura/scripts/oura.py brief",
        "Oura brief"
    )
    results['oura'] = {
        'success': oura_result and oura_result.returncode == 0,
        'time': oura_time,
        'exit_code': oura_result.returncode if oura_result else None
    }
    
    # 3. Mirror
    log_subsection("TESTING: Mirror")
    mirror_result, mirror_time = safe_run_command(
        "python3 /data/workspace/skills/mirror/scripts/mirror.py",
        "Mirror question generation"
    )
    results['mirror'] = {
        'success': mirror_result and mirror_result.returncode == 0,
        'time': mirror_time,
        'exit_code': mirror_result.returncode if mirror_result else None
    }
    
    # 4. WhatsApp test (just check if message command works)
    log_subsection("TESTING: WhatsApp Messaging")
    # Test with a dry run first
    whatsapp_result, whatsapp_time = safe_run_command(
        "python3 -c \"from message import message; print('Message tool available')\"",
        "WhatsApp messaging capability check"
    )
    results['whatsapp'] = {
        'success': whatsapp_result and whatsapp_result.returncode == 0,
        'time': whatsapp_time,
        'exit_code': whatsapp_result.returncode if whatsapp_result else None
    }
    
    return results

def main():
    print(f"🐚 MORNING BRIEFING DEBUG - {datetime.now().isoformat()}")
    print("Running as SUBAGENT to compare against cron execution")
    print(f"Python version: {sys.version}")
    print(f"Running from: {__file__}")
    
    # Step 1: Environment analysis
    log_environment()
    
    # Step 2: Component testing
    results = test_morning_briefing_components()
    
    # Step 3: Summary
    log_section("EXECUTION SUMMARY")
    
    total_time = 0
    for component, data in results.items():
        status = "✅ SUCCESS" if data['success'] else "❌ FAILED"
        print(f"{component.upper():12} | {status:12} | {data['time']:.3f}s | Exit: {data['exit_code']}")
        total_time += data['time']
    
    print(f"\nTotal execution time: {total_time:.3f} seconds")
    print(f"All components successful: {all(r['success'] for r in results.values())}")
    
    # Save results for comparison
    debug_result = {
        'timestamp': datetime.now().isoformat(),
        'execution_type': 'subagent',
        'results': results,
        'total_time': total_time,
        'success': all(r['success'] for r in results.values()),
        'environment': {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'user_id': os.getuid(),
            'group_id': os.getgid()
        }
    }
    
    debug_file = '/data/workspace/morning_briefing_debug.json'
    with open(debug_file, 'w') as f:
        json.dump(debug_result, f, indent=2)
    
    print(f"\n📊 Debug results saved to: {debug_file}")
    
    return all(r['success'] for r in results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
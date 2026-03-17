#!/usr/bin/env python3
"""
Welly Daemon - Proper background service for Welly Always-On monitoring

This creates a proper daemon process that's completely detached from the parent terminal
and won't exit when shell sessions end.
"""

import os
import sys
import time
import signal
import atexit
import asyncio
import logging
from pathlib import Path

class WellyDaemon:
    def __init__(self, pidfile='/data/workspace/welly/welly-daemon.pid'):
        self.pidfile = pidfile
    
    def daemonize(self):
        """Fork and create daemon process"""
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                # Exit parent process
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"Fork #1 failed: {err}\n")
            sys.exit(1)
        
        # Decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        # Second fork
        try:
            pid = os.fork()
            if pid > 0:
                # Exit second parent process
                sys.exit(0)
        except OSError as err:
            sys.stderr.write(f"Fork #2 failed: {err}\n")
            sys.exit(1)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open('/data/workspace/memory/welly-daemon.log', 'a+')
        se = open('/data/workspace/memory/welly-daemon.log', 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        # Write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(f"{pid}\n")
    
    def delpid(self):
        """Remove pidfile"""
        try:
            os.remove(self.pidfile)
        except:
            pass
    
    def start(self):
        """Start the daemon"""
        # Check for a pidfile to see if daemon is already running
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            pid = None
        
        if pid:
            try:
                os.kill(pid, 0)  # Check if process is running
                print("Welly daemon already running")
                sys.exit(1)
            except OSError:
                # Process doesn't exist, remove stale pidfile
                os.remove(self.pidfile)
        
        # Start the daemon
        self.daemonize()
        self.run()
    
    def stop(self):
        """Stop the daemon"""
        # Get PID from pidfile
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
        except IOError:
            print("Welly daemon not running")
            return
        
        # Try to kill the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            if "No such process" in str(err):
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                print("Welly daemon stopped")
            else:
                print(f"Failed to stop daemon: {err}")
                sys.exit(1)
    
    def restart(self):
        """Restart the daemon"""
        self.stop()
        time.sleep(1)
        self.start()
    
    def status(self):
        """Check daemon status"""
        try:
            with open(self.pidfile, 'r') as pf:
                pid = int(pf.read().strip())
            
            try:
                os.kill(pid, 0)
                print(f"Welly daemon running (PID: {pid})")
                return True
            except OSError:
                print("Welly daemon not running (stale pidfile)")
                os.remove(self.pidfile)
                return False
        except IOError:
            print("Welly daemon not running")
            return False
    
    def run(self):
        """Main daemon process - runs the actual Welly monitor"""
        # Setup logging for daemon
        logging.basicConfig(
            filename='/data/workspace/memory/welly-daemon.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        print(f"Welly daemon started (PID: {os.getpid()})")
        logging.info(f"Welly daemon started (PID: {os.getpid()})")
        
        # Change to welly directory
        os.chdir('/data/workspace/welly')
        
        # Import and run the actual monitor
        try:
            # Import welly-monitor.py using importlib
            import importlib.util
            spec = importlib.util.spec_from_file_location("welly_monitor", "/data/workspace/welly/welly-monitor.py")
            welly_monitor_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(welly_monitor_module)
            WellyMonitor = welly_monitor_module.WellyMonitor
            
            def signal_handler(signum, frame):
                logging.info("Received shutdown signal")
                print("Shutting down Welly daemon")
                sys.exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Run the monitor
            monitor = WellyMonitor()
            asyncio.run(monitor.run())
            
        except Exception as e:
            logging.error(f"Welly daemon error: {e}")
            print(f"Welly daemon error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    daemon = WellyDaemon()
    
    if len(sys.argv) == 2:
        command = sys.argv[1]
        if command == 'start':
            print("Starting Welly daemon...")
            daemon.start()
        elif command == 'stop':
            daemon.stop()
        elif command == 'restart':
            daemon.restart()
        elif command == 'status':
            daemon.status()
        else:
            print(f"Unknown command: {command}")
            print("Usage: python3 welly-daemon.py {start|stop|restart|status}")
            sys.exit(2)
    else:
        print("Usage: python3 welly-daemon.py {start|stop|restart|status}")
        sys.exit(2)
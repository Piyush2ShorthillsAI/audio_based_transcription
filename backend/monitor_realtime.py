#!/usr/bin/env python3
"""Real-time server monitoring"""

import subprocess
import time
import signal
import sys

def monitor_server():
    """Monitor server logs in real-time"""
    print("🔍 REAL-TIME SERVER MONITORING")
    print("=" * 40)
    print("📋 Monitoring uvicorn server for 500 errors...")
    print("🎯 Now try the frontend - I'll capture the exact error!")
    print("Press Ctrl+C to stop monitoring")
    print("-" * 40)
    
    try:
        # Find the server process
        result = subprocess.run(['pgrep', '-f', 'uvicorn.*main:app'], capture_output=True, text=True)
        if result.stdout.strip():
            server_pid = result.stdout.strip().split('\n')[0]
            print(f"📍 Found server process: PID {server_pid}")
        else:
            print("❌ Server not found!")
            return
            
        # Monitor server output in real-time
        process = subprocess.Popen(['tail', '-f', '/proc/{}/fd/1'.format(server_pid)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT, 
                                 universal_newlines=True,
                                 bufsize=1)
        
        def signal_handler(signum, frame):
            print("\n👋 Stopping monitor...")
            process.terminate()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        while True:
            line = process.stdout.readline()
            if line:
                timestamp = time.strftime("%H:%M:%S", time.localtime())
                if "ERROR" in line or "500" in line or "traceback" in line.lower():
                    print(f"🔥 [{timestamp}] ERROR: {line.strip()}")
                elif "INFO" in line and ("POST /audio/" in line or "upload" in line):
                    print(f"📤 [{timestamp}] REQUEST: {line.strip()}")
                elif any(keyword in line.lower() for keyword in ["exception", "failed", "error"]):
                    print(f"⚠️  [{timestamp}] WARNING: {line.strip()}")
                elif line.strip():
                    print(f"📋 [{timestamp}] LOG: {line.strip()}")
            else:
                time.sleep(0.1)
                
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        print("💡 Try manual log checking instead")

if __name__ == "__main__":
    monitor_server()
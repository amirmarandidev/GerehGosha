# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Unified Service Runner
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
# ==============================================================================

import subprocess
import time
import sys
import os
import platform
import sqlite3

def init_auth_db_if_needed():
    """Ensure auth.db exists and active credentials are displayed so user is never locked out."""
    try:
        if sys.platform == 'win32':
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except Exception:
                pass

        import importlib.util
        cli_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gerehgosha-cli.py")
        if os.path.exists(cli_file):
            spec = importlib.util.spec_from_file_location("gerehgosha_cli", cli_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.ensure_admin()
    except Exception as e:
        pass

def kill_process_tree(proc):
    """Cleanly terminate process and all child processes on Windows & Linux."""
    if not proc:
        return
    try:
        pid = proc.pid
        if platform.system() == 'Windows':
            subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            proc.terminate()
            try:
                proc.wait(timeout=2)
            except:
                proc.kill()
    except Exception:
        pass

def run_service(name, cmd, cwd=None):
    print(f"Starting {name}...")
    return subprocess.Popen(cmd, shell=True, cwd=cwd)

if __name__ == "__main__":
    print("==============================================================")
    print("   GerehGosha (گره‌گشا) Unified Core Engine")
    print("   Developed by Amir (@amirmarandidev)")
    print("==============================================================")
    
    init_auth_db_if_needed()
    
    procs = []
    try:
        # Start Gateway (Port 5000)
        procs.append(run_service("GerehGosha Gateway", f'"{sys.executable}" gateway.py', cwd=os.getcwd()))
        
        # Start GerehGosha Tor Engine (Port 54322)
        tor_dir = os.path.join(os.getcwd(), "pasarguard-tor")
        procs.append(run_service("GerehGosha Tor Engine", f'"{sys.executable}" api.py', cwd=tor_dir))
        
        # Note: GerehGosha Secondary carrier is currently isolated in offline standby
        
        print("\n[+] GerehGosha services started successfully.")
        print("[+] Unified Gateway: http://127.0.0.1:5000")
        print("[+] Direct Engine  : http://127.0.0.1:54322")
        print("[!] Press Ctrl+C to stop all services simultaneously.\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[!] Stopping all services...")
        for p in procs:
            kill_process_tree(p)
            
        if platform.system() == 'Windows':
            subprocess.run("taskkill /F /IM tor.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("[OK] All services stopped.")
        sys.exit(0)

# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - High-Performance Admin & System CLI Console
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
# ==============================================================================

__author__ = "Amir (@amirmarandidev)"
__copyright__ = "Copyright (c) 2024-2026 Amir. All rights reserved."
__project__ = "GerehGosha (گره‌گشا)"
__version__ = "2.6.2-CLI"

import os
import sys
import sqlite3
import secrets
import string
import platform
import subprocess
import socket
import json
import urllib.request
import urllib.parse
import ssl
from werkzeug.security import generate_password_hash, check_password_hash

# Ensure UTF-8 output on Windows consoles
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Enable Windows ANSI Virtual Terminal Processing for rich colors
if platform.system() == 'Windows':
    os.system('')

# ANSI Colors
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_RED = "\033[1;31m"
CLR_GREEN = "\033[1;32m"
CLR_YELLOW = "\033[1;33m"
CLR_BLUE = "\033[1;34m"
CLR_MAGENTA = "\033[1;35m"
CLR_CYAN = "\033[1;36m"
CLR_WHITE = "\033[1;37m"
CLR_DIM = "\033[2m"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "auth.db")
CRED_FILE = os.path.join(BASE_DIR, "credentials.txt")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT)")
        conn.commit()

def generate_secure_password(length=16):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    # Ensure at least one upper, lower, digit, and symbol
    pwd = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    pwd += [secrets.choice(alphabet) for _ in range(length - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return ''.join(pwd)

def get_all_users():
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users ORDER BY username ASC")
        return [row[0] for row in cursor.fetchall()]

def print_banner():
    print(f"\n{CLR_CYAN}=============================================================={CLR_RESET}")
    print(f"{CLR_CYAN}       GerehGosha (گره‌گشا) - System & Admin Management CLI    {CLR_RESET}")
    print(f"{CLR_DIM}          Architected & Engineered by Amir (@amirmarandidev)   {CLR_RESET}")
    print(f"{CLR_CYAN}=============================================================={CLR_RESET}")

def print_cred_box(username, password, title="ADMIN CREDENTIALS"):
    box_w = 48
    print(f"\n{CLR_YELLOW}┌" + "─" * box_w + f"┐{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_BOLD}  🔐 {title:<42}{CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}├" + "─" * box_w + f"┤{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}  👤 Username : {CLR_CYAN}{username:<33}{CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}  🔑 Password : {CLR_GREEN}{password:<33}{CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}  🌐 Dashboard: {CLR_WHITE}{'http://127.0.0.1:5000':<33}{CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}└" + "─" * box_w + f"┘{CLR_RESET}")
    
    # Save to local credentials.txt for safe offline retrieval
    try:
        with open(CRED_FILE, "w", encoding="utf-8") as f:
            f.write("====================================================\n")
            f.write("      GerehGosha (گره‌گشا) - Admin Credentials      \n")
            f.write("      Developed by Amir (@amirmarandidev)          \n")
            f.write("====================================================\n")
            f.write(f"Username     : {username}\n")
            f.write(f"Password     : {password}\n")
            f.write(f"Dashboard URL: http://127.0.0.1:5000\n")
            f.write(f"Tor Direct   : http://127.0.0.1:54322\n")
            f.write("====================================================\n")
    except Exception:
        pass

def show_credentials():
    """Inspect and display active credentials or guide user."""
    init_db()
    users = get_all_users()
    if not users:
        print(f"\n{CLR_RED}[!] No admin accounts found in auth.db!{CLR_RESET}")
        print(f"{CLR_YELLOW}👉 Creating default admin credentials (admin / admin123)...{CLR_RESET}")
        add_admin("admin", "admin123")
        return

    # 1. Check if credentials.txt exists and matches an existing user
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, "r", encoding="utf-8") as f:
                content = f.read()
            u_val, p_val = None, None
            for line in content.splitlines():
                if "Username" in line and ":" in line:
                    u_val = line.split(":", 1)[1].strip()
                elif "Password" in line and ":" in line:
                    p_val = line.split(":", 1)[1].strip()
            
            if u_val and p_val and u_val in users:
                with sqlite3.connect(DB_PATH) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (u_val,))
                    row = cursor.fetchone()
                    if row and check_password_hash(row[0], p_val):
                        print_cred_box(u_val, p_val, title="ACTIVE ADMIN CREDENTIALS")
                        print(f" {CLR_DIM}📄 Verified from credentials.txt{CLR_RESET}\n")
                        return
        except Exception:
            pass

    # 2. Test if default 'admin123' matches any active admin
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password_hash FROM users")
        for u, h in cursor.fetchall():
            if check_password_hash(h, "admin123"):
                print_cred_box(u, "admin123", title="ACTIVE ADMIN CREDENTIALS")
                print(f" {CLR_DIM}📄 Verified default password & saved to credentials.txt{CLR_RESET}\n")
                return

    # 3. If password was changed and not in credentials.txt
    print(f"\n{CLR_YELLOW}┌────────────────────────────────────────────────────────┐{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_BOLD}  ℹ️  EXISTING ADMIN ACCOUNTS DETECTED                  {CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}├────────────────────────────────────────────────────────┤{CLR_RESET}")
    for u in users:
        print(f"{CLR_YELLOW}│{CLR_RESET}  👤 Account : {CLR_CYAN}{u:<41}{CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}  🔑 Passwords are encrypted with secure hashes.        {CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}  💡 To reset password, use Option [4] or run:          {CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}│{CLR_RESET}     {CLR_GREEN}python gerehgosha-cli.py --reset-user <username>{CLR_RESET}    {CLR_YELLOW}│{CLR_RESET}")
    print(f"{CLR_YELLOW}└────────────────────────────────────────────────────────┘{CLR_RESET}\n")

def ensure_admin():
    """Ensures an admin exists and displays active credentials."""
    init_db()
    users = get_all_users()
    if not users:
        add_admin("admin", "admin123")
    else:
        show_credentials()

def list_admins():
    users = get_all_users()
    print(f"\n{CLR_BOLD}📋 Registered Admin Accounts ({len(users)} total):{CLR_RESET}")
    print(f"{CLR_DIM}--------------------------------------------------------------{CLR_RESET}")
    if not users:
        print(f" {CLR_RED}[!] No admin accounts found in auth.db!{CLR_RESET}")
        print(f" {CLR_YELLOW}👉 Tip: Use option (2) to create your first admin account.{CLR_RESET}")
    else:
        for idx, u in enumerate(users, 1):
            print(f"  {CLR_CYAN}[{idx}]{CLR_RESET} 👤 {CLR_WHITE}{u}{CLR_RESET}")
    print(f"{CLR_DIM}--------------------------------------------------------------{CLR_RESET}\n")

def add_admin(username=None, password=None):
    users = get_all_users()
    if not username:
        suggested = "admin" if not users else f"admin_{secrets.randbelow(900) + 100}"
        inp = input(f"Enter username [{suggested}]: ").strip()
        username = inp if inp else suggested

    if username in users:
        print(f"{CLR_RED}[!] Error: Username '{username}' already exists.{CLR_RESET}")
        return False

    if not password:
        choice = input("Auto-generate secure password? [Y/n]: ").strip().lower()
        if choice in ['', 'y', 'yes']:
            password = generate_secure_password(16)
        else:
            import getpass
            password = getpass.getpass("Enter password: ")
            if not password:
                print(f"{CLR_RED}[!] Password cannot be empty.{CLR_RESET}")
                return False

    hashed = generate_password_hash(password)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()

    print(f"\n{CLR_GREEN}[+] Admin user '{username}' created successfully!{CLR_RESET}")
    print_cred_box(username, password)
    return True

def reset_password(target_user=None, new_pass=None):
    users = get_all_users()
    if not users:
        print(f"{CLR_RED}[!] No users exist to change password. Add one first.{CLR_RESET}")
        return False

    if not target_user:
        print(f"\n{CLR_BOLD}Select user to reset password:{CLR_RESET}")
        for idx, u in enumerate(users, 1):
            print(f"  [{idx}] {u}")
        choice = input(f"Enter number [1-{len(users)}] or username: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(users):
            target_user = users[int(choice) - 1]
        elif choice in users:
            target_user = choice
        else:
            print(f"{CLR_RED}[!] Invalid user selection.{CLR_RESET}")
            return False

    if not new_pass:
        gen_choice = input(f"Auto-generate new password for '{target_user}'? [Y/n]: ").strip().lower()
        if gen_choice in ['', 'y', 'yes']:
            new_pass = generate_secure_password(16)
        else:
            import getpass
            new_pass = getpass.getpass(f"Enter new password for '{target_user}': ")
            if not new_pass:
                print(f"{CLR_RED}[!] Password cannot be empty.{CLR_RESET}")
                return False

    hashed = generate_password_hash(new_pass)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed, target_user))
        conn.commit()

    print(f"\n{CLR_GREEN}[+] Password for '{target_user}' updated successfully!{CLR_RESET}")
    print_cred_box(target_user, new_pass, title=f"UPDATED CREDENTIALS: {target_user}")
    return True

def delete_admin():
    users = get_all_users()
    if not users:
        print(f"{CLR_RED}[!] No users found.{CLR_RESET}")
        return

    if len(users) <= 1:
        print(f"{CLR_YELLOW}[!] Warning: There is only 1 admin account ('{users[0]}').{CLR_RESET}")
        print(f"{CLR_RED}[!] Deleting the last admin would lock you out. Please add another user before deleting this one.{CLR_RESET}")
        return

    print(f"\n{CLR_BOLD}Select user to delete:{CLR_RESET}")
    for idx, u in enumerate(users, 1):
        print(f"  [{idx}] {u}")
    choice = input(f"Enter number [1-{len(users)}] or username: ").strip()
    target_user = None
    if choice.isdigit() and 1 <= int(choice) <= len(users):
        target_user = users[int(choice) - 1]
    elif choice in users:
        target_user = choice

    if not target_user:
        print(f"{CLR_RED}[!] Invalid user selection.{CLR_RESET}")
        return

    confirm = input(f"{CLR_RED}Are you sure you want to permanently delete admin '{target_user}'? [y/N]: {CLR_RESET}").strip().lower()
    if confirm in ['y', 'yes']:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("DELETE FROM users WHERE username = ?", (target_user,))
            conn.commit()
        print(f"{CLR_GREEN}[+] User '{target_user}' has been deleted.{CLR_RESET}")
    else:
        print("Cancelled.")

def check_port(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def inspect_network():
    print(f"\n{CLR_BOLD}🔍 System & Network Health Diagnostic:{CLR_RESET}")
    print(f"{CLR_DIM}--------------------------------------------------------------{CLR_RESET}")
    
    # 1. Check Gateway (Port 5000)
    gw_alive = check_port("127.0.0.1", 5000)
    gw_status = f"{CLR_GREEN}● ONLINE (Port 5000){CLR_RESET}" if gw_alive else f"{CLR_RED}○ OFFLINE{CLR_RESET}"
    print(f"  🛡️ GerehGosha Gateway   : {gw_status}")
    print(f"     URL                  : {CLR_CYAN}http://127.0.0.1:5000{CLR_RESET}")

    # 2. Check Tor Engine (Port 54322)
    tor_alive = check_port("127.0.0.1", 54322)
    tor_status = f"{CLR_GREEN}● ONLINE (Port 54322){CLR_RESET}" if tor_alive else f"{CLR_RED}○ OFFLINE{CLR_RESET}"
    print(f"  ⚡ Tor Traffic Engine   : {tor_status}")
    print(f"     URL                  : {CLR_CYAN}http://127.0.0.1:54322{CLR_RESET}")

    # 3. Resolve Public IP
    print(f"\n  🌍 Resolving Server Public IP...")
    pub_ip = "Unknown"
    for srv in ["https://api.ipify.org", "http://checkip.amazonaws.com", "https://icanhazip.com"]:
        try:
            req = urllib.request.Request(srv, headers={'User-Agent': 'curl/7.68.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                pub_ip = resp.read().decode('utf-8').strip()
                break
        except Exception:
            continue
    print(f"     Public WAN IP        : {CLR_YELLOW}{pub_ip}{CLR_RESET}")
    if pub_ip != "Unknown":
        print(f"     External Access URL  : {CLR_CYAN}http://{pub_ip}:5000{CLR_RESET}")

    # 4. Show Registered Admin count
    users = get_all_users()
    print(f"\n  👤 Registered Admins    : {CLR_WHITE}{len(users)}{CLR_RESET} ({', '.join(users) if users else 'None'})")
    if os.path.exists(CRED_FILE):
        print(f"  📄 Saved Credentials    : {CLR_DIM}{CRED_FILE}{CLR_RESET}")
    print(f"{CLR_DIM}--------------------------------------------------------------{CLR_RESET}\n")

def fetch_pasarguard_token():
    print(f"\n{CLR_CYAN}=============================================================={CLR_RESET}")
    print(f"{CLR_CYAN}             PasarGuard Admin Token Fetcher                   {CLR_RESET}")
    print(f"{CLR_CYAN}=============================================================={CLR_RESET}")
    host = input("Enter PasarGuard Host/IP [127.0.0.1]: ").strip() or "127.0.0.1"
    port = input("Enter PasarGuard Port [54321]: ").strip() or "54321"
    user = input("Enter PasarGuard Username: ").strip()
    import getpass
    pwd = getpass.getpass("Enter PasarGuard Password: ")

    data = urllib.parse.urlencode({'username': user, 'password': pwd}).encode('utf-8')
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for proto in ['https', 'http']:
        url = f"{proto}://{host}:{port}/api/admin/token"
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                if resp.status == 200:
                    res = json.loads(resp.read().decode())
                    token = res.get('access_token')
                    if token:
                        print(f"\n{CLR_GREEN}[+] SUCCESS! Your PasarGuard Admin API Token:{CLR_RESET}\n")
                        print(f"{CLR_WHITE}{token}{CLR_RESET}\n")
                        return token
        except Exception:
            pass

    print(f"\n{CLR_RED}[!] Failed to fetch token. Verify credentials and ensure PasarGuard is running on {host}:{port}.{CLR_RESET}\n")
    return None

def flush_tor_cache():
    print("\n[*] Cleaning Tor temporary state and caches...")
    base_dirs = [os.path.join(BASE_DIR, "tor_data"), os.path.join(BASE_DIR, "assets", "tor_data"), os.path.join(BASE_DIR, "pasarguard-tor", "tor_data")]
    import shutil
    flushed = 0
    for bd in base_dirs:
        if os.path.exists(bd):
            try:
                shutil.rmtree(bd, ignore_errors=True)
                os.makedirs(bd, exist_ok=True)
                flushed += 1
            except Exception as e:
                print(f"Error flushing {bd}: {e}")
    print(f"{CLR_GREEN}[+] Tor cache flushed successfully ({flushed} directories reset).{CLR_RESET}\n")

def update_gerehgosha():
    print(f"\n{CLR_CYAN}=============================================================={CLR_RESET}")
    print(f"{CLR_CYAN}       GerehGosha (گره‌گشا) - Automated System Updater        {CLR_RESET}")
    print(f"{CLR_CYAN}=============================================================={CLR_RESET}")
    
    # 1. Protect database and credentials
    print(f"{CLR_YELLOW}[*] Backing up local credentials and database...{CLR_RESET}")
    import shutil
    tmp_dir = "/tmp" if platform.system() != 'Windows' else os.environ.get('TEMP', '.')
    if os.path.exists(DB_PATH):
        try:
            shutil.copy2(DB_PATH, os.path.join(tmp_dir, "auth.db.bak"))
        except Exception:
            pass
    if os.path.exists(CRED_FILE):
        try:
            shutil.copy2(CRED_FILE, os.path.join(tmp_dir, "credentials.txt.bak"))
        except Exception:
            pass

    # 2. Git Stash before pull to ensure clean working tree
    print(f"{CLR_YELLOW}[*] Stashing local modifications...{CLR_RESET}")
    subprocess.run(["git", "stash"], cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 3. Git Pull
    print(f"{CLR_YELLOW}[*] Pulling latest code from Git repository...{CLR_RESET}")
    try:
        branch_res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=BASE_DIR, capture_output=True, text=True)
        branch = branch_res.stdout.strip() or "master"
    except Exception:
        branch = "master"

    pull_res = subprocess.run(["git", "pull", "origin", branch], cwd=BASE_DIR)
    if pull_res.returncode != 0:
        print(f"{CLR_YELLOW}[!] Branch-specific pull returned error. Attempting standard git pull...{CLR_RESET}")
        subprocess.run(["git", "pull"], cwd=BASE_DIR)

    # 4. Stash again to keep working directory clean
    print(f"{CLR_YELLOW}[*] Stashing local state...{CLR_RESET}")
    subprocess.run(["git", "stash"], cwd=BASE_DIR, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 5. Restore database if needed
    bak_db = os.path.join(tmp_dir, "auth.db.bak")
    if os.path.exists(bak_db) and not os.path.exists(DB_PATH):
        shutil.copy2(bak_db, DB_PATH)

    # 6. If on Linux, chmod +x install.sh and run in AUTO_UPDATE mode
    if platform.system() != 'Windows':
        install_script = os.path.join(BASE_DIR, "install.sh")
        if os.path.exists(install_script):
            print(f"{CLR_GREEN}[*] Setting execution permissions and launching installer...{CLR_RESET}")
            os.system(f"chmod +x '{install_script}'")
            env = os.environ.copy()
            env["AUTO_UPDATE"] = "1"
            subprocess.run(["/bin/bash", install_script], cwd=BASE_DIR, env=env)
            sys.exit(0)
    else:
        print(f"\n{CLR_GREEN}[+] Git pull and update completed successfully!{CLR_RESET}\n")

def main_interactive():
    init_db()
    while True:
        print_banner()
        users = get_all_users()
        user_info = f"{len(users)} registered" if users else "NO ADMIN CREATED"
        user_color = CLR_GREEN if users else CLR_RED
        
        print(f" Current Admins: {user_color}[{user_info}]{CLR_RESET}")
        print()
        print(f"  {CLR_CYAN}1.{CLR_RESET} 🔐 View Current Admin Credentials")
        print(f"  {CLR_CYAN}2.{CLR_RESET} 📋 List All Admin Accounts")
        print(f"  {CLR_CYAN}3.{CLR_RESET} ➕ Add New Admin Account")
        print(f"  {CLR_CYAN}4.{CLR_RESET} 🔑 Reset / Change Admin Password")
        print(f"  {CLR_CYAN}5.{CLR_RESET} 🗑️ Delete Admin Account")
        print(f"  {CLR_CYAN}6.{CLR_RESET} 🔍 System & Network Diagnostic")
        print(f"  {CLR_CYAN}7.{CLR_RESET} 🎫 Fetch PasarGuard API Token")
        print(f"  {CLR_CYAN}8.{CLR_RESET} 🧹 Flush Tor Cache & State")
        print(f"  {CLR_CYAN}9.{CLR_RESET} 🔄 Update GerehGosha (Git Pull & Upgrade)")
        print(f"  {CLR_CYAN}0.{CLR_RESET} 🚪 Exit")
        print(f"{CLR_CYAN}=============================================================={CLR_RESET}")
        
        choice = input("Select an option [0-9]: ").strip()
        if choice == '1':
            show_credentials()
            input("Press Enter to continue...")
        elif choice == '2':
            list_admins()
            input("Press Enter to continue...")
        elif choice == '3':
            add_admin()
            input("Press Enter to continue...")
        elif choice == '4':
            reset_password()
            input("Press Enter to continue...")
        elif choice == '5':
            delete_admin()
            input("Press Enter to continue...")
        elif choice == '6':
            inspect_network()
            input("Press Enter to continue...")
        elif choice == '7':
            fetch_pasarguard_token()
            input("Press Enter to continue...")
        elif choice == '8':
            flush_tor_cache()
            input("Press Enter to continue...")
        elif choice == '9':
            update_gerehgosha()
            input("Press Enter to continue...")
        elif choice in ['0', 'q', 'exit']:
            print(f"\n{CLR_CYAN}Goodbye! ✨{CLR_RESET}\n")
            sys.exit(0)
        else:
            print(f"{CLR_RED}Invalid option. Please choose [0-9].{CLR_RESET}")

def parse_cli_args():
    """Support headless CLI operations: python gerehgosha-cli.py --add-user <user> --password <pass>"""
    import argparse
    parser = argparse.ArgumentParser(description="GerehGosha Management CLI")
    parser.add_argument("--version", action="version", version=f"GerehGosha CLI v{__version__}")
    parser.add_argument("--list", action="store_true", help="List all registered admin users")
    parser.add_argument("--add-user", type=str, help="Username to create")
    parser.add_argument("--password", type=str, help="Password for user (auto-generated if omitted)")
    parser.add_argument("--reset-user", type=str, help="Username whose password to reset")
    parser.add_argument("--status", action="store_true", help="Inspect system and port health")
    parser.add_argument("--flush-cache", action="store_true", help="Flush Tor cache")
    parser.add_argument("--update", action="store_true", help="Pull latest updates from Git and execute upgrade")
    parser.add_argument("--seed-default", action="store_true", help="Create default admin if none exists")
    parser.add_argument("--show-credentials", action="store_true", help="Display active admin credentials")
    parser.add_argument("--ensure-admin", action="store_true", help="Ensure an admin exists and display credentials")
    args = parser.parse_args()

    if args.show_credentials:
        show_credentials()
        return True
    if args.ensure_admin or args.seed_default:
        ensure_admin()
        return True
    if args.list:
        list_admins()
        return True
    if args.add_user:
        add_admin(args.add_user, args.password)
        return True
    if args.reset_user:
        reset_password(args.reset_user, args.password)
        return True
    if args.status:
        inspect_network()
        return True
    if args.flush_cache:
        flush_tor_cache()
        return True
    if args.update:
        update_gerehgosha()
        return True
    return False

if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1:
        if not parse_cli_args():
            main_interactive()
    else:
        main_interactive()

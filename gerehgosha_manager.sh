#!/bin/bash

# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - System Manager & Maintenance CLI
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
#  Notice: Unauthorized redistribution, removal of copyright notices, or
#          reverse engineering of this software is strictly prohibited.
# ==============================================================================

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit
fi

APP_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
GATEWAY_SERVICE_FILE="/etc/systemd/system/gerehgosha.service"

update_gerehgosha() {
    echo ""
    echo "====================================="
    echo "      UPDATING GEREHGOSHA            "
    echo "====================================="
    cd "$APP_DIR" || exit 1

    echo -e "\033[1;33m[*] Backing up databases and credentials to prevent data loss...\033[0m"
    if [ -f "$APP_DIR/auth.db" ]; then
        cp -f "$APP_DIR/auth.db" "/tmp/auth.db.bak"
    fi
    if [ -f "$APP_DIR/credentials.txt" ]; then
        cp -f "$APP_DIR/credentials.txt" "/tmp/credentials.txt.bak"
    fi
    if [ -f "$APP_DIR/assets/config.json" ]; then
        cp -f "$APP_DIR/assets/config.json" "/tmp/tor_config.json.bak"
    elif [ -f "$APP_DIR/pasarguard-tor/config.json" ]; then
        cp -f "$APP_DIR/pasarguard-tor/config.json" "/tmp/tor_config.json.bak"
    fi

    echo -e "\033[1;33m[*] Stashing local modifications...\033[0m"
    git stash 2>/dev/null || true

    echo -e "\033[1;33m[*] Pulling latest code from Git...\033[0m"
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "master")
    if git pull origin "$CURRENT_BRANCH"; then
        echo -e "\033[1;32m[+] Git pull completed successfully.\033[0m"
    else
        echo -e "\033[1;33m[!] Specific branch pull failed, trying standard git pull...\033[0m"
        git pull || true
    fi

    echo -e "\033[1;33m[*] Stashing local state to ensure clean working tree...\033[0m"
    git stash 2>/dev/null || true

    # Restore preserved auth.db and credentials if missing
    if [ -f "/tmp/auth.db.bak" ]; then
        cp -f "/tmp/auth.db.bak" "$APP_DIR/auth.db"
    fi
    if [ -f "/tmp/credentials.txt.bak" ]; then
        cp -f "/tmp/credentials.txt.bak" "$APP_DIR/credentials.txt"
    fi

    echo -e "\033[1;33m[*] Setting execution permissions on installer scripts...\033[0m"
    chmod +x "$APP_DIR/install.sh"
    chmod +x "$APP_DIR/gerehgosha_manager.sh"

    echo -e "\033[1;32m[*] Running installer to apply updates without data loss...\033[0m"
    AUTO_UPDATE=1 "$APP_DIR/install.sh"
    exit 0
}

# Check for CLI arguments (e.g. gerehgosha update)
if [ "$1" == "update" ] || [ "$1" == "--update" ]; then
    update_gerehgosha
fi

install_services() {
    echo "====================================="
    echo " Installing GerehGosha Tor Engine..."
    echo "====================================="
    if [ -f "$APP_DIR/assets/install_service.sh" ]; then
        chmod +x "$APP_DIR/assets/install_service.sh"
        cd "$APP_DIR/assets" && ./install_service.sh
        cd "$APP_DIR"
    elif [ -f "$APP_DIR/pasarguard-tor/install_service.sh" ]; then
        chmod +x "$APP_DIR/pasarguard-tor/install_service.sh"
        cd "$APP_DIR/pasarguard-tor" && ./install_service.sh
        cd "$APP_DIR"
    else
        echo "Error: assets/install_service.sh not found."
    fi

    # GerehGosha Secondary carrier is isolated and skipped in active installation

    echo "====================================="
    echo " Installing Unified Gateway Service..."
    echo "====================================="
    
    # Check if python3 is available
    if ! command -v python3 &> /dev/null; then
        echo "Installing Python3 and required packages..."
        apt-get update && apt-get install -y python3 python3-pip
    fi

    # Install Python requirements for Gateway
    pip3 install flask requests werkzeug --break-system-packages --ignore-installed

    # Create systemd service for gateway
    cat > "$GATEWAY_SERVICE_FILE" <<EOF
[Unit]
Description=GerehGosha Unified Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/gateway.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
Alias=gerehgosha-gateway.service
EOF

    systemctl daemon-reload
    systemctl enable gerehgosha.service
    systemctl start gerehgosha.service

    echo "====================================="
    echo "GerehGosha Gateway has been installed!"
    echo "Gateway is running on Port 5000."
    echo "Direct Tor Panel on Port 54322."
    echo "====================================="
}

manage_admins() {
    echo "====================================="
    if [ -f "$APP_DIR/gerehgosha-cli.py" ]; then
        python3 "$APP_DIR/gerehgosha-cli.py"
    else
        echo "Error: gerehgosha-cli.py not found."
    fi
}

view_logs() {
    echo "====================================="
    echo "Viewing Gateway Logs (Press Ctrl+C to exit)..."
    journalctl -u gerehgosha.service -f
}

fetch_pg_token() {
    echo ""
    echo "====================================="
    echo "     Pasarguard Token Fetcher        "
    echo "====================================="
    read -p "Enter Pasarguard IP/Host (Default 127.0.0.1): " pg_host
    pg_host=${pg_host:-127.0.0.1}
    read -p "Enter Pasarguard Port (Default 54321): " pg_port
    pg_port=${pg_port:-54321}
    read -p "Enter Pasarguard Username: " pg_user
    read -sp "Enter Pasarguard Password: " pg_pass
    echo ""

    # Python script to fetch the token
    python3 -c "
import urllib.request
import urllib.parse
import json
import ssl

def fetch(proto):
    url = f'{proto}://$pg_host:$pg_port/api/admin/token'
    data = urllib.parse.urlencode({'username': '$pg_user', 'password': '$pg_pass'}).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
        if response.status == 200:
            resp_data = json.loads(response.read().decode())
            return resp_data.get('access_token')
    return None

try:
    token = fetch('https')
    if token: print(f'\n\033[1;32m[+] SUCCESS! Your Admin API Token:\033[0m\n\n{token}\n')
except Exception:
    try:
        token = fetch('http')
        if token: print(f'\n\033[1;32m[+] SUCCESS! Your Admin API Token:\033[0m\n\n{token}\n')
        else: print('\n[!] Logged in, but token not found in response.')
    except urllib.error.HTTPError as e:
        print(f'\n\033[1;31m[!] Login failed. Check your username/password. (HTTP {e.code})\033[0m')
    except Exception as e:
        print(f'\n\033[1;31m[!] Connection error: {e}. Is Pasarguard running on port $pg_port?\033[0m')
"
}

uninstall_services() {
    echo ""
    echo "====================================="
    echo "      UNINSTALLING GEREHGOSHA        "
    echo "====================================="
    read -p "Are you sure you want to completely remove GerehGosha and all its services? (y/n): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "Uninstallation cancelled."
        return
    fi

    echo "Stopping and disabling services..."
    systemctl stop gerehgosha.service gerehgosha-gateway.service pepepanel-gateway.service tor-checker.service pepeshark.service 2>/dev/null
    systemctl disable gerehgosha.service gerehgosha-gateway.service pepepanel-gateway.service tor-checker.service pepeshark.service 2>/dev/null

    echo "Removing systemd service files..."
    rm -f /etc/systemd/system/gerehgosha.service
    rm -f /etc/systemd/system/gerehgosha-gateway.service
    rm -f /etc/systemd/system/pepepanel-gateway.service
    rm -f /etc/systemd/system/tor-checker.service
    rm -f /etc/systemd/system/pepeshark.service
    systemctl daemon-reload

    echo "Removing global command aliases..."
    rm -f /usr/local/bin/gerehgosha
    rm -f /usr/local/bin/pepeshark

    read -p "Do you also want to DELETE all application files in $APP_DIR? (y/n): " confirm_files
    if [[ "$confirm_files" == "y" || "$confirm_files" == "Y" ]]; then
        echo "Deleting application files..."
        rm -rf "$APP_DIR"
        echo "====================================="
        echo "GerehGosha has been completely uninstalled."
        echo "====================================="
        exit 0
    else
        echo "====================================="
        echo "Services uninstalled. Files were kept in $APP_DIR."
        echo "====================================="
    fi
}

while true; do
    echo ""
    echo "====================================="
    echo "    GerehGosha (گره‌گشا) Manager     "
    echo "   Developed by Amir (@amirmarandidev) "
    echo "====================================="
    echo "1. Install All Services (Tor Engine & Gateway)"
    echo "2. Manage Admins (Add/View users)"
    echo "3. View System Logs (Gateway)"
    echo "4. Restart Gateway Service"
    echo "5. Restart GerehGosha Engine (Tor)"
    echo "6. Update GerehGosha (Git Pull & Seamless Upgrade)"
    echo "7. Fetch Pasarguard Token"
    echo "8. Uninstall GerehGosha"
    echo "9. Exit"
    echo "====================================="
    read -p "Select an option [1-9]: " option

    case $option in
        1) install_services ;;
        2) manage_admins ;;
        3) view_logs ;;
        4) systemctl restart gerehgosha.service; echo "Gateway Restarted." ;;
        5) systemctl restart tor-checker.service; echo "GerehGosha Tor Engine Restarted." ;;
        6) update_gerehgosha ;;
        7) fetch_pg_token ;;
        8) uninstall_services ;;
        9) echo "Exiting..."; exit 0 ;;
        *) echo "Invalid option." ;;
    esac
done

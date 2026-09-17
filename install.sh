#!/bin/bash

# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Unified Traffic Engine & Gateway Installer
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
#  Notice: Unauthorized redistribution, removal of copyright notices, or
#          reverse engineering of this software is strictly prohibited.
# ==============================================================================

# ANSI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}================================================================${NC}"
echo -e "${CYAN}        GerehGosha (گره‌گشا) Unified Gateway Installer          ${NC}"
echo -e "${CYAN}              Developed by Amir (@amirmarandidev)               ${NC}"
echo -e "${CYAN}================================================================${NC}"

# Handle @ symbol if used in installation (e.g. bash -c "$(curl ...)" @ install)
if [ "${1:-}" = "@" ]; then
    shift
fi

ACTION="${1:-install}"
if [ "$ACTION" == "update" ] || [ "$ACTION" == "--update" ]; then
    export AUTO_UPDATE="1"
fi

# 1. Check Root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run this script as root (use sudo).${NC}"
  exit 1
fi

# 2. Variables & Directories
INSTALL_DIR="/opt/gerehgosha"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" 2>/dev/null && pwd )"
REPO_URL="https://github.com/amirmarandidev/GerehGosha.git"

# Detect if running remotely via curl/pipe without repository files
if [ ! -f "$SCRIPT_DIR/gateway.py" ]; then
    echo -e "${CYAN}[*] Remote execution detected. Setting up GerehGosha repository...${NC}"
    if ! command -v git >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
        apt-get update -y -q > /dev/null 2>&1 || true
        apt-get install -y -q git curl wget > /dev/null 2>&1 || true
    fi

    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${CYAN}[*] Cloning GerehGosha into $INSTALL_DIR...${NC}"
        mkdir -p "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
    elif [ ! -d "$INSTALL_DIR/.git" ]; then
        echo -e "${CYAN}[*] Initializing Git repository in $INSTALL_DIR...${NC}"
        TMP_DIR=$(mktemp -d)
        git clone "$REPO_URL" "$TMP_DIR"
        cp -rn "$TMP_DIR/." "$INSTALL_DIR/" 2>/dev/null || cp -rf "$TMP_DIR/." "$INSTALL_DIR/"
        rm -rf "$TMP_DIR"
    else
        echo -e "${CYAN}[*] Pulling latest updates into $INSTALL_DIR...${NC}"
        cd "$INSTALL_DIR"
        git pull origin master > /dev/null 2>&1 || true
    fi

    find "$INSTALL_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true
    chmod +x "$INSTALL_DIR/install.sh" 2>/dev/null || true
    chmod +x "$INSTALL_DIR/gerehgosha.sh" 2>/dev/null || true
    chmod +x "$INSTALL_DIR/gerehgosha_manager.sh" 2>/dev/null || true
    cd "$INSTALL_DIR"
    exec bash "$INSTALL_DIR/install.sh" "$@"
fi

# Detect legacy /opt/pepepanel directory and offer seamless migration
if [ -d "/opt/pepepanel" ] && [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}[*] Migrating legacy /opt/pepepanel directory to $INSTALL_DIR...${NC}"
    mv /opt/pepepanel "$INSTALL_DIR"
fi

echo -e "\n${YELLOW}[*] Installing system dependencies (curl, wget, python3, pip, sqlite3, tor)...${NC}"
apt-get update -y -q > /dev/null 2>&1
apt-get install -y -q curl wget tar python3 python3-pip python3-venv sqlite3 tor geoip-database libevent-dev psmisc > /dev/null 2>&1
systemctl stop tor > /dev/null 2>&1 || true
systemctl disable tor > /dev/null 2>&1 || true

# 3. Handle Existing Installation & Copy Project Files
KEEP_DB="n"
if [ "$AUTO_UPDATE" == "1" ]; then
    KEEP_DB="y"
    if [ -f "$INSTALL_DIR/auth.db" ]; then
        cp -f "$INSTALL_DIR/auth.db" "/tmp/auth.db.bak" 2>/dev/null || true
    fi
    echo -e "${GREEN}[+] Auto-Update Mode: Preserving existing admin accounts (auth.db)${NC}"
    if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}[*] Copying updated files to $INSTALL_DIR...${NC}"
        mkdir -p "$INSTALL_DIR"
        cp -rf "$SCRIPT_DIR/." "$INSTALL_DIR/"
    fi
elif [ -d "$INSTALL_DIR" ]; then
    if [ "$SCRIPT_DIR" != "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}[!] GerehGosha is already installed at $INSTALL_DIR.${NC}"
        read -p "Do you want to overwrite the existing installation? [y/N]: " overwrite
        if [[ "$overwrite" != "y" && "$overwrite" != "Y" ]]; then
            echo -e "${RED}[*] Installation aborted by user.${NC}"
            exit 0
        fi
        
        if [ -f "$INSTALL_DIR/auth.db" ]; then
            read -p "Do you want to KEEP existing admin accounts? (auth.db) [Y/n]: " keep_db_input
            if [[ "$keep_db_input" != "n" && "$keep_db_input" != "N" ]]; then
                KEEP_DB="y"
                cp "$INSTALL_DIR/auth.db" "/tmp/auth.db.bak"
                echo -e "${GREEN}[+] Backed up auth.db${NC}"
            fi
        fi
        
        echo -e "${YELLOW}[*] Copying files to $INSTALL_DIR...${NC}"
        mkdir -p "$INSTALL_DIR"
        cp -rf "$SCRIPT_DIR/." "$INSTALL_DIR/"
    else
        # Running directly inside /opt/gerehgosha
        if [ -f "$INSTALL_DIR/auth.db" ]; then
            read -p "Do you want to KEEP existing admin accounts? (auth.db) [Y/n]: " keep_db_input
            if [[ "$keep_db_input" != "n" && "$keep_db_input" != "N" ]]; then
                KEEP_DB="y"
            fi
        fi
    fi
else
    echo -e "${YELLOW}[*] Installing GerehGosha to $INSTALL_DIR...${NC}"
    mkdir -p "$INSTALL_DIR"
    cp -rf "$SCRIPT_DIR/." "$INSTALL_DIR/"
fi

# Fix Windows CRLF line endings on all scripts
find "$INSTALL_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true

# Set execution permissions
chmod +x "$INSTALL_DIR/install.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/gerehgosha_manager.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/assets/install_service.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/assets/setup_and_run.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/pasarguard-tor/install_service.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/pasarguard-tor/setup_and_run.sh" 2>/dev/null || true
chmod +x "$INSTALL_DIR/gerehgosha-carrier/install.sh" 2>/dev/null || true

cd "$INSTALL_DIR"

if [ "$KEEP_DB" == "y" ] && [ -f "/tmp/auth.db.bak" ]; then
    mv "/tmp/auth.db.bak" "$INSTALL_DIR/auth.db"
    echo -e "${GREEN}[+] Restored existing auth.db${NC}"
fi

# 4. Setup Python Environment for Gateway
echo -e "\n${YELLOW}[*] Setting up Python environment...${NC}"
apt-get install -y -q python3-flask python3-requests python3-werkzeug > /dev/null 2>&1 || true
pip3 install flask requests werkzeug --break-system-packages > /dev/null 2>&1 || true

# 5. Execute Sub-Installer (GerehGosha Tor Engine)
echo -e "${YELLOW}[*] Executing sub-installer for GerehGosha Tor Engine...${NC}"

# Terminate any lingering background engine processes from old versions
pkill -9 -f "api.py" > /dev/null 2>&1 || true

# Maintain backward-compatibility symlink so legacy services never crash
if [ ! -e "$INSTALL_DIR/pasarguard-tor" ] && [ -d "$INSTALL_DIR/assets" ]; then
    ln -s "$INSTALL_DIR/assets" "$INSTALL_DIR/pasarguard-tor" 2>/dev/null || true
fi

if [ -f "$INSTALL_DIR/assets/install_service.sh" ]; then
    chmod +x "$INSTALL_DIR/assets/install_service.sh"
    cd "$INSTALL_DIR/assets" && ./install_service.sh
    cd "$INSTALL_DIR"
elif [ -f "$INSTALL_DIR/pasarguard-tor/install_service.sh" ]; then
    chmod +x "$INSTALL_DIR/pasarguard-tor/install_service.sh"
    cd "$INSTALL_DIR/pasarguard-tor" && ./install_service.sh
    cd "$INSTALL_DIR"
fi
systemctl daemon-reload 2>/dev/null || true
systemctl restart tor-checker 2>/dev/null || true
# GerehGosha Secondary carrier is isolated and excluded from active installation

# 6. Auto-Generate Secure Admin Credentials (if no DB exists)
if [ "$KEEP_DB" != "y" ] || [ ! -f "$INSTALL_DIR/auth.db" ]; then
    echo -e "${YELLOW}[*] Generating secure admin credentials...${NC}"
    USERNAME="admin_$((RANDOM % 900 + 100))"
    PASSWORD=$(tr -dc 'A-Za-z0-9!@#$%^&*' </dev/urandom | head -c 16)

    ADMIN_USER="$USERNAME" ADMIN_PASS="$PASSWORD" python3 -c "
import os, sqlite3
from werkzeug.security import generate_password_hash

user = os.environ.get('ADMIN_USER')
pwd = os.environ.get('ADMIN_PASS')
conn = sqlite3.connect('auth.db')
conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password_hash TEXT, preferred_language TEXT)')
hashed = generate_password_hash(pwd)
conn.execute('INSERT OR REPLACE INTO users (username, password_hash) VALUES (?, ?)', (user, hashed))
conn.commit()
conn.close()
"
else
    echo -e "${GREEN}[+] Existing admin credentials preserved.${NC}"
fi

# 7. Setup Systemd Service for Gateway
echo -e "${YELLOW}[*] Setting up Gateway systemd service (gerehgosha.service)...${NC}"
cat > "/etc/systemd/system/gerehgosha.service" <<EOF
[Unit]
Description=GerehGosha Unified Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/gateway.py
Restart=always
RestartSec=5
LimitNOFILE=1048576
LimitNPROC=1048576

[Install]
WantedBy=multi-user.target
Alias=gerehgosha-gateway.service
EOF

# Clean up legacy services if present
systemctl stop pepepanel-gateway.service > /dev/null 2>&1 || true
systemctl disable pepepanel-gateway.service > /dev/null 2>&1 || true
rm -f /etc/systemd/system/pepepanel-gateway.service

systemctl daemon-reload
systemctl enable gerehgosha.service > /dev/null 2>&1
systemctl restart gerehgosha.service

# 8. Global Command Alias
echo -e "${YELLOW}[*] Creating global 'gerehgosha' command...${NC}"
cat > /usr/local/bin/gerehgosha <<EOF
#!/bin/bash
cd $INSTALL_DIR
./gerehgosha_manager.sh "\$@"
EOF
chmod +x /usr/local/bin/gerehgosha

# Clean up legacy command aliases
rm -f /usr/local/bin/pepeshark 2>/dev/null || true

SERVER_IP=$(curl -s --connect-timeout 5 http://checkip.amazonaws.com || curl -s --connect-timeout 5 https://api.ipify.org || hostname -I | awk '{print $1}')

# 9. Final Output
echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}             GerehGosha (گره‌گشا) Installed Successfully!        ${NC}"
echo -e "${GREEN}                 Developed by Amir (@amirmarandidev)            ${NC}"
echo -e "${GREEN}================================================================${NC}"
echo -e "🌐 Dashboard Login: ${CYAN}http://$SERVER_IP:5000${NC}"
echo -e "⚡ Direct Core    : ${CYAN}http://$SERVER_IP:54322${NC}"
echo -e ""
echo -e "${YELLOW}--- 🔐 ADMIN CREDENTIALS ---${NC}"
if [ "$KEEP_DB" != "y" ] || [ -n "$USERNAME" ]; then
    echo -e "👤 Username : ${RED}$USERNAME${NC}"
    echo -e "🔑 Password : ${RED}$PASSWORD${NC}"
else
    echo -e "${GREEN}Preserved from previous installation.${NC}"
fi
echo -e "${YELLOW}----------------------------${NC}"
echo -e ""
echo -e "⚙️ To manage the panel in the future, simply type: ${CYAN}gerehgosha${NC}"
echo -e "⚡ Systemd status command: ${CYAN}systemctl status gerehgosha${NC}"
echo -e "${CYAN}================================================================${NC}\n"

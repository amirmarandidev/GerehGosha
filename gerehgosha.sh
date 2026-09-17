#!/usr/bin/env bash
# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Master One-Line Installer & Manager
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  GitHub             : https://github.com/amirmarandidev/GerehGosha
#  Copyright (c) 2024-2026 Amir. All rights reserved.
# ==============================================================================
set -e

# Handle @ symbol if used in installation (e.g. bash -c "$(curl ...)" @ install)
if [ "${1:-}" = "@" ]; then
    shift
fi

ACTION="${1:-install}"
INSTALL_DIR="/opt/gerehgosha"
REPO_URL="https://github.com/amirmarandidev/GerehGosha.git"

# ANSI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[1;36m'
NC='\033[0m'

# Check Root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Please run this script as root (use sudo).${NC}"
    exit 1
fi

bootstrap_repo() {
    echo -e "${CYAN}[*] Checking and installing prerequisites (git, curl, wget)...${NC}"
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

    # Fix execution permissions
    find "$INSTALL_DIR" -type f \( -name "*.sh" -o -name "*.py" \) -exec sed -i 's/\r$//' {} + 2>/dev/null || true
    chmod +x "$INSTALL_DIR/install.sh" 2>/dev/null || true
    chmod +x "$INSTALL_DIR/gerehgosha.sh" 2>/dev/null || true
    chmod +x "$INSTALL_DIR/gerehgosha_manager.sh" 2>/dev/null || true
}

case "$ACTION" in
    install|--install|-i)
        bootstrap_repo
        cd "$INSTALL_DIR"
        exec bash "$INSTALL_DIR/install.sh"
        ;;
    update|--update|-u)
        bootstrap_repo
        if [ -f "$INSTALL_DIR/gerehgosha_manager.sh" ]; then
            cd "$INSTALL_DIR"
            exec bash "$INSTALL_DIR/gerehgosha_manager.sh" update
        else
            cd "$INSTALL_DIR"
            AUTO_UPDATE=1 exec bash "$INSTALL_DIR/install.sh"
        fi
        ;;
    uninstall|--uninstall)
        echo -e "${YELLOW}[*] Stopping and removing GerehGosha services...${NC}"
        systemctl stop gerehgosha.service gerehgosha-gateway.service pepepanel-gateway.service tor-checker.service 2>/dev/null || true
        systemctl disable gerehgosha.service gerehgosha-gateway.service pepepanel-gateway.service tor-checker.service 2>/dev/null || true
        rm -f /etc/systemd/system/gerehgosha.service /etc/systemd/system/tor-checker.service /etc/systemd/system/pepepanel-gateway.service
        systemctl daemon-reload
        rm -f /usr/local/bin/gerehgosha
        
        read -p "Do you also want to delete all files in $INSTALL_DIR? (y/N): " rm_files
        if [[ "$rm_files" == "y" || "$rm_files" == "Y" ]]; then
            rm -rf "$INSTALL_DIR"
            echo -e "${GREEN}[+] GerehGosha has been completely removed.${NC}"
        else
            echo -e "${GREEN}[+] Services removed. Files kept in $INSTALL_DIR.${NC}"
        fi
        ;;
    status|--status|-s)
        if [ -f "$INSTALL_DIR/gerehgosha-cli.py" ]; then
            python3 "$INSTALL_DIR/gerehgosha-cli.py" --status
        else
            echo -e "${RED}[!] GerehGosha is not installed at $INSTALL_DIR${NC}"
        fi
        ;;
    cli|menu|*)
        bootstrap_repo
        if [ -f "$INSTALL_DIR/gerehgosha_manager.sh" ]; then
            cd "$INSTALL_DIR"
            exec bash "$INSTALL_DIR/gerehgosha_manager.sh"
        else
            cd "$INSTALL_DIR"
            exec bash "$INSTALL_DIR/install.sh"
        fi
        ;;
esac

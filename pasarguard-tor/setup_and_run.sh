#!/bin/bash

# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Tor Engine Startup & Runtime Runner
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
# ==============================================================================

echo "=============================================================="
echo "   GerehGosha (گره‌گشا) Tor Engine (Linux)"
echo "   Engineered by Amir (@amirmarandidev)"
echo "=============================================================="
echo ""

# Ensure system dependencies and Tor are installed
if ! command -v tor >/dev/null 2>&1; then
    echo "Tor binary not found. Installing via apt..."
    if [ "$EUID" -ne 0 ]; then
        sudo apt-get update -y && sudo apt-get install -y tor geoip-database libevent-dev psmisc
    else
        apt-get update -y && apt-get install -y tor geoip-database libevent-dev psmisc
    fi
fi

# Stop default OS Tor service to prevent port conflicts with our multi-instance manager
systemctl stop tor > /dev/null 2>&1 || true
systemctl disable tor > /dev/null 2>&1 || true

# Check for python3
if ! command -v python3 >/dev/null 2>&1; then
    echo "[Error] python3 is not installed! Please install python3."
    exit 1
fi

# Check for pip3
if ! command -v pip3 >/dev/null 2>&1; then
    echo "[!] pip3 is not installed. Attempting to install python3-pip..."
    if [ "$EUID" -ne 0 ]; then
        sudo apt-get update && sudo apt-get install -y python3-pip
    else
        apt-get update && apt-get install -y python3-pip
    fi
fi

echo "Step 1: Installing Python requirements..."
pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1 || pip3 install -r requirements.txt > /dev/null 2>&1 || true
echo "[OK] Requirements checked."
echo ""

echo "Step 2: Cleaning up any hanging background processes..."
pkill -9 -f "python api.py" > /dev/null 2>&1 || true
pkill -9 -f "python3 api.py" > /dev/null 2>&1 || true
pkill -9 -f "python tor_manager.py" > /dev/null 2>&1 || true
pkill -9 -f "python3 tor_manager.py" > /dev/null 2>&1 || true
pkill -9 -x "tor" > /dev/null 2>&1 || true
if command -v fuser >/dev/null 2>&1; then
    fuser -k 54322/tcp > /dev/null 2>&1 || true
fi

echo "Cleaning up old cache and state files (preventing OS conflicts)..."
rm -rf ./tor_data > /dev/null 2>&1 || true
rm -f tor_fingerprints_cache.json > /dev/null 2>&1 || true
sleep 1
echo ""

echo "Step 3: Launching Web Panel (FastAPI)..."
echo "The panel will be available at http://127.0.0.1:54322"
ulimit -n 65535 > /dev/null 2>&1 || true
exec python3 api.py


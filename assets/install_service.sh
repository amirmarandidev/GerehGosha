#!/bin/bash

# ==============================================================================
#  GEREHGOSHA (گره‌گشا) - Engine Service Installer
# ==============================================================================
#  Author / Developer : Amir (@amirmarandidev)
#  Telegram           : https://t.me/amirmarandidev
#  Email              : amirmarandidev@gmail.com
#  Copyright (c) 2024-2026 Amir. All rights reserved.
# ==============================================================================

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (sudo bash install_service.sh)"
  exit
fi

# Get the absolute path to the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_PATH="/etc/systemd/system/tor-checker.service"

echo "Installing GerehGosha Tor Engine Systemd Service..."
echo "Project Directory: $DIR"

# Generate the systemd service file dynamically
cat <<EOF > $SERVICE_PATH
[Unit]
Description=GerehGosha (گره‌گشا) Tor Engine Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DIR
ExecStart=/bin/bash setup_and_run.sh
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
LimitNOFILE=1048576
LimitNPROC=1048576

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable/start the service
systemctl daemon-reload
systemctl enable tor-checker
systemctl restart tor-checker

echo ""
echo "============================================================"
echo "✅ Tor Checker is now running permanently in the background!"
echo "============================================================"
echo ""
echo "Helpful Commands:"
echo "  - Check Status: systemctl status tor-checker"
echo "  - Stop Service: systemctl stop tor-checker"
echo "  - Start Service: systemctl start tor-checker"
echo "  - View Live Logs: journalctl -u tor-checker -f"
echo "============================================================"

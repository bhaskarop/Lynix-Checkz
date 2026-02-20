#!/bin/bash

# ========================================
#  Lynix Checker Bot — Auto Setup Script
#  Installs deps + creates systemd service
# ========================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "██╗     ██╗   ██╗███╗   ██╗██╗██╗  ██╗"
echo "██║     ╚██╗ ██╔╝████╗  ██║██║╚██╗██╔╝"
echo "██║      ╚████╔╝ ██╔██╗ ██║██║ ╚███╔╝ "
echo "██║       ╚██╔╝  ██║╚██╗██║██║ ██╔██╗ "
echo "███████╗   ██║   ██║ ╚████║██║██╔╝ ██╗"
echo "╚══════╝   ╚═╝   ╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝"
echo -e "${NC}"
echo -e "${GREEN}Lynix Checker Bot — Auto Setup${NC}"
echo "========================================"

# Get current directory
BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVICE_NAME="lynix-bot"
PYTHON_BIN=""

# ── Check root ──
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[!] Please run as root: sudo bash setup.sh${NC}"
    exit 1
fi

# ── Update system ──
echo -e "\n${YELLOW}[1/5] Updating system packages...${NC}"
apt-get update -y && apt-get upgrade -y

# ── Install Python & pip ──
echo -e "\n${YELLOW}[2/5] Installing Python3 & pip...${NC}"
apt-get install -y python3 python3-pip python3-venv

# ── Setup virtual environment ──
echo -e "\n${YELLOW}[3/5] Setting up virtual environment...${NC}"
if [ ! -d "$BOT_DIR/venv" ]; then
    python3 -m venv "$BOT_DIR/venv"
    echo -e "${GREEN}[✓] Virtual environment created${NC}"
else
    echo -e "${GREEN}[✓] Virtual environment already exists${NC}"
fi

PYTHON_BIN="$BOT_DIR/venv/bin/python3"
PIP_BIN="$BOT_DIR/venv/bin/pip"

# ── Install dependencies ──
echo -e "\n${YELLOW}[4/5] Installing Python dependencies...${NC}"
$PIP_BIN install --upgrade pip
$PIP_BIN install -r "$BOT_DIR/req.txt"

# ── Create systemd service ──
echo -e "\n${YELLOW}[5/5] Creating systemd service...${NC}"

cat > /etc/systemd/system/${SERVICE_NAME}.service <<EOF
[Unit]
Description=Lynix Checker Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${BOT_DIR}
ExecStart=${PYTHON_BIN} ${BOT_DIR}/main.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

# Environment
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# ── Enable & start service ──
systemctl daemon-reload
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

echo ""
echo "========================================"
echo -e "${GREEN}[✓] Setup complete! Bot is now running.${NC}"
echo "========================================"
echo ""
echo -e "  ${CYAN}Commands:${NC}"
echo -e "  Start   → ${GREEN}sudo systemctl start ${SERVICE_NAME}${NC}"
echo -e "  Stop    → ${RED}sudo systemctl stop ${SERVICE_NAME}${NC}"
echo -e "  Restart → ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "  Status  → ${CYAN}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "  Logs    → ${CYAN}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo ""

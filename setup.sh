#!/bin/bash

# ============================================
# ZUNEX BOT - Setup Script
# ============================================
# Developer: MR ZUYAN
# Team: XVSOULX
# GitHub: https://github.com/ZUYANx/zunex-telegram-bot
# ============================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║   ███████╗██╗   ██╗███╗   ██╗███████╗██╗  ██╗          ║"
echo "║   ╚══███╔╝██║   ██║████╗  ██║██╔════╝╚██╗██╔╝          ║"
echo "║     ███╔╝ ██║   ██║██╔██╗ ██║█████╗   ╚███╔╝           ║"
echo "║    ███╔╝  ██║   ██║██║╚██╗██║██╔══╝   ██╔██╗           ║"
echo "║   ███████╗╚██████╔╝██║ ╚████║███████╗██╔╝ ██╗          ║"
echo "║   ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝          ║"
echo "║                                                          ║"
echo "║              BOT - Order Management System              ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}ZUNEX BOT INSTALLATION SCRIPT${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if running on Termux/Android
if [ -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}Detected: Termux (Android)${NC}"
    IS_TERMUX=true
else
    echo -e "${YELLOW}Detected: Linux/Unix${NC}"
    IS_TERMUX=false
fi

# Step 1: Update and install dependencies
echo -e "${BLUE}Step 1/6: Installing dependencies...${NC}"

if [ "$IS_TERMUX" = true ]; then
    echo -e "${YELLOW}Termux detected. Installing packages...${NC}"
    pkg update -y
    pkg upgrade -y
    pkg install -y python python-pip git sqlite
else
    echo -e "${YELLOW}Linux detected. Installing packages...${NC}"
    sudo apt-get update -y
    sudo apt-get install -y python3 python3-pip git sqlite3
fi

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Step 2: Install Python packages
echo -e "${BLUE}Step 2/6: Installing Python packages...${NC}"

# Create requirements.txt if not exists
cat > requirements.txt << 'EOF'
requests>=2.28.0
sqlalchemy>=2.0.0
python-telegram-bot>=20.0.0
EOF

pip install -r requirements.txt
echo -e "${GREEN}✓ Python packages installed${NC}"

# Step 3: Create global command
echo -e "${BLUE}Step 3/6: Creating global command 'zunex'...${NC}"

# Get current directory
INSTALL_DIR=$(pwd)

# Create the wrapper script
cat > /data/data/com.termux/files/usr/bin/zunex << 'EOF'
#!/bin/bash
# ZUNEX Bot Launcher

# Get the installation directory
INSTALL_DIR="/storage/emulated/0/TELEGRAM-BOT"

# Check if installation directory exists
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Error: ZUNEX Bot not found at $INSTALL_DIR"
    echo "Please run setup.sh first"
    exit 1
fi

# Change to installation directory
cd "$INSTALL_DIR"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found in $INSTALL_DIR"
    exit 1
fi

# Check for internet connection
echo "Checking internet connection..."
if ! ping -c 1 8.8.8.8 > /dev/null 2>&1; then
    echo "Warning: No internet connection"
    echo "Bot will wait for connection..."
fi

# Run the bot with Python
python3 main.py
EOF

# Make it executable
chmod +x /data/data/com.termux/files/usr/bin/zunex

echo -e "${GREEN}✓ Global command 'zunex' created${NC}"

# Step 4: Verify installation
echo -e "${BLUE}Step 4/6: Verifying installation...${NC}"

if command -v zunex &> /dev/null; then
    echo -e "${GREEN}✓ 'zunex' command is available globally${NC}"
else
    echo -e "${YELLOW}Warning: 'zunex' command may not be in PATH${NC}"
    echo -e "${YELLOW}Try restarting terminal or run: source ~/.bashrc${NC}"
fi

# Step 5: Create .bashrc alias (if not exists)
echo -e "${BLUE}Step 5/6: Adding alias to .bashrc...${NC}"

if [ "$IS_TERMUX" = true ]; then
    BASHRC="$HOME/.bashrc"
else
    BASHRC="$HOME/.bashrc"
fi

if ! grep -q "alias zunex=" "$BASHRC" 2>/dev/null; then
    echo "" >> "$BASHRC"
    echo "# ZUNEX Bot Alias" >> "$BASHRC"
    echo "alias zunex='cd $INSTALL_DIR && python3 main.py'" >> "$BASHRC"
    echo -e "${GREEN}✓ Alias added to .bashrc${NC}"
else
    echo -e "${YELLOW}Alias already exists in .bashrc${NC}"
fi

# Step 6: Create startup script
echo -e "${BLUE}Step 6/6: Creating startup script...${NC}"

cat > start_bot.sh << 'EOF'
#!/bin/bash
# ZUNEX Bot Startup Script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if already running
if pgrep -f "python.*main.py" > /dev/null; then
    echo "ZUNEX Bot is already running"
    echo "To stop: pkill -f 'python.*main.py'"
    exit 1
fi

# Start the bot
echo "Starting ZUNEX Bot..."
nohup python3 main.py > bot.log 2>&1 &

# Get the PID
PID=$!
echo "Bot started with PID: $PID"
echo "Log file: bot.log"
echo "To view logs: tail -f bot.log"
echo "To stop: kill $PID"
EOF

chmod +x start_bot.sh
echo -e "${GREEN}✓ Startup script created${NC}"

# Final message
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}INSTALLATION COMPLETE!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

echo -e "${YELLOW}How to use:${NC}"
echo "─────────────────────────────────────────────────"
echo ""
echo -e "${BLUE}1. Run bot:${NC}"
echo "   zunex"
echo ""
echo -e "${BLUE}2. Or using script:${NC}"
echo "   ./start_bot.sh"
echo ""
echo -e "${BLUE}3. To stop bot:${NC}"
echo "   Press Ctrl+C"
echo "   or kill -9 PID"
echo ""
echo -e "${BLUE}4. View logs:${NC}"
echo "   tail -f bot.log"
echo ""
echo -e "${BLUE}5. Update bot:${NC}"
echo "   git pull"
echo ""
echo -e "${YELLOW}Commands available:${NC}"
echo "─────────────────────────────────────────────────"
echo -e "${GREEN}/start${NC}    - Welcome message"
echo -e "${GREEN}/setup${NC}    - Configure business"
echo -e "${GREEN}/add${NC}      - Add new product"
echo -e "${GREEN}/sku${NC}      - View product details"
echo -e "${GREEN}/today${NC}    - Today's orders"
echo -e "${GREEN}/sr${NC}       - Search orders"
echo ""
echo -e "${YELLOW}Order Format:${NC}"
echo "─────────────────────────────────────────────────"
echo "Phone: 01712345678"
echo "Address: Dhaka, Bangladesh"
echo "SKU: ZX-001"
echo "Qty: 1"
echo "Price: 1000"
echo "Size: XL (optional)"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Bot is ready! Type 'zunex' to start${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

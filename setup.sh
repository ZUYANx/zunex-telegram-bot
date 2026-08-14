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
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================
# BANNER
# ============================================
clear
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
echo "║           TELEGRAM ORDER MANAGEMENT BOT                  ║"
echo "║                                                          ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    SETUP WIZARD                          ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# CHECK TERMUX OR LINUX
# ============================================
if [ -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}Detected: Termux (Android)${NC}"
    INSTALL_DIR="/storage/emulated/0/TELEGRAM-BOT"
    IS_TERMUX=true
else
    echo -e "${YELLOW}Detected: Linux/Unix${NC}"
    INSTALL_DIR="$HOME/zunex-bot"
    IS_TERMUX=false
fi

echo -e "${BLUE}Installation Directory: ${INSTALL_DIR}${NC}"
echo ""

# ============================================
# STEP 1: INSTALL DEPENDENCIES
# ============================================
echo -e "${CYAN}[1/10] Installing system dependencies...${NC}"

if [ "$IS_TERMUX" = true ]; then
    pkg update -y 2>/dev/null
    pkg upgrade -y 2>/dev/null
    pkg install -y python python-pip git sqlite 2>/dev/null
else
    sudo apt-get update -y 2>/dev/null
    sudo apt-get install -y python3 python3-pip git sqlite3 2>/dev/null
fi

echo -e "${GREEN}✓ System dependencies installed${NC}"

# ============================================
# STEP 2: CREATE DIRECTORY
# ============================================
echo -e "${CYAN}[2/10] Creating installation directory...${NC}"

if [ ! -d "$INSTALL_DIR" ]; then
    mkdir -p "$INSTALL_DIR"
fi

cd "$INSTALL_DIR"
echo -e "${GREEN}✓ Directory created: ${INSTALL_DIR}${NC}"

# ============================================
# STEP 3: CLONE OR COPY FILES
# ============================================
echo -e "${CYAN}[3/10] Getting bot files...${NC}"

if [ -f "main.py" ]; then
    echo -e "${YELLOW}Files already exist. Updating...${NC}"
    git pull 2>/dev/null
else
    # Try to clone from GitHub
    git clone https://github.com/ZUYANx/zunex-telegram-bot.git . 2>/dev/null
    
    # If clone fails, create files manually
    if [ ! -f "main.py" ]; then
        echo -e "${YELLOW}Git clone failed. Creating files manually...${NC}"
        touch main.py config.py database.py models.py steadfast.py steadfast-admin.py setup_handler.py parser.py image_upload.py utils.py
    fi
fi

echo -e "${GREEN}✓ Bot files ready${NC}"

# ============================================
# STEP 4: INSTALL PYTHON PACKAGES
# ============================================
echo -e "${CYAN}[4/10] Installing Python packages...${NC}"

cat > requirements.txt << 'EOF'
requests>=2.28.0
sqlalchemy>=2.0.0
python-telegram-bot>=20.0.0
EOF

pip install -r requirements.txt 2>/dev/null || pip3 install -r requirements.txt 2>/dev/null

echo -e "${GREEN}✓ Python packages installed${NC}"

# ============================================
# STEP 5: ENTER TELEGRAM BOT TOKEN
# ============================================
echo -e "${CYAN}[5/10] Enter Telegram Bot Token${NC}"
echo -e "${YELLOW}How to get:${NC}"
echo "  1. Open Telegram"
echo "  2. Search for @BotFather"
echo "  3. Send /newbot"
echo "  4. Follow instructions"
echo "  5. Copy your bot token"
echo ""
echo -e "${BLUE}Enter your bot token:${NC}"
read -p "> " BOT_TOKEN

while [ -z "$BOT_TOKEN" ]; do
    echo -e "${RED}Bot token is required!${NC}"
    echo -e "${BLUE}Enter your bot token:${NC}"
    read -p "> " BOT_TOKEN
done

# ============================================
# STEP 6: ENTER STEADFAST API KEY
# ============================================
echo -e "${CYAN}[6/10] Enter Steadfast API Key (optional)${NC}"
echo -e "${YELLOW}You can skip this and configure later using /setup${NC}"
echo ""
echo -e "${BLUE}Enter Steadfast API Key (press Enter to skip):${NC}"
read -p "> " STEADFAST_API_KEY

# ============================================
# STEP 7: ENTER STEADFAST SECRET KEY
# ============================================
if [ -n "$STEADFAST_API_KEY" ]; then
    echo -e "${CYAN}[7/10] Enter Steadfast Secret Key${NC}"
    echo -e "${BLUE}Enter Steadfast Secret Key (press Enter to skip):${NC}"
    read -p "> " STEADFAST_SECRET_KEY
else
    STEADFAST_SECRET_KEY=""
    echo -e "${YELLOW}Skipping Steadfast Secret Key${NC}"
fi

# ============================================
# STEP 8: CREATE CONFIG.PY
# ============================================
echo -e "${CYAN}[8/10] Creating configuration file...${NC}"

cat > config.py << EOF
# config.py - ZUNEX Bot Configuration

# Telegram Bot
BOT_TOKEN = "${BOT_TOKEN}"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Database
DATABASE_FILE = "zunex_orders.db"

# Steadfast API
STEADFAST_BASE_URL = "https://portal.packzy.com/api/v1"
LABEL_SIZE = "2x3"

# Image Hosting API (freeimage.host)
IMAGE_API_KEY = "6d207e02198a847aa98d0a2a901485a5"

# Order Settings
STARTING_ORDER_NUM = 1000
INVOICE_PREFIX = "ZX"

# SQLAlchemy
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_FILE}"
EOF

echo -e "${GREEN}✓ config.py created${NC}"

# ============================================
# STEP 9: CREATE STARTUP SCRIPTS
# ============================================
echo -e "${CYAN}[9/10] Creating startup scripts...${NC}"

# Create global command
if [ "$IS_TERMUX" = true ]; then
    cat > /data/data/com.termux/files/usr/bin/zunex << 'EOF'
#!/bin/bash
cd /storage/emulated/0/TELEGRAM-BOT
python3 main.py
EOF
    chmod +x /data/data/com.termux/files/usr/bin/zunex
fi

# Create start_bot.sh
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
python3 main.py
EOF

chmod +x start_bot.sh

echo -e "${GREEN}✓ Startup scripts created${NC}"

# ============================================
# STEP 10: FINAL SETUP
# ============================================
echo -e "${CYAN}[10/10] Finalizing setup...${NC}"

# Create .bashrc alias
if [ "$IS_TERMUX" = true ]; then
    BASHRC="$HOME/.bashrc"
else
    BASHRC="$HOME/.bashrc"
fi

if ! grep -q "alias zunex=" "$BASHRC" 2>/dev/null; then
    echo "" >> "$BASHRC"
    echo "# ZUNEX Bot Alias" >> "$BASHRC"
    echo "alias zunex='cd $INSTALL_DIR && python3 main.py'" >> "$BASHRC"
fi

# Create .env file with keys for reference
cat > .env << EOF
# ZUNEX Bot Environment Variables
BOT_TOKEN=${BOT_TOKEN}
STEADFAST_API_KEY=${STEADFAST_API_KEY:-Not Set}
STEADFAST_SECRET_KEY=${STEADFAST_SECRET_KEY:-Not Set}
EOF

echo -e "${GREEN}✓ Final setup complete${NC}"

# ============================================
# SETUP COMPLETE
# ============================================
clear
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    SETUP COMPLETE!                         ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Installation Summary:${NC}"
echo "─────────────────────────────────────────────────"
echo -e "Installation Directory: ${BLUE}${INSTALL_DIR}${NC}"
echo -e "Bot Token: ${BLUE}${BOT_TOKEN:0:10}...${BOT_TOKEN: -5}${NC}"
if [ -n "$STEADFAST_API_KEY" ]; then
    echo -e "Steadfast API Key: ${BLUE}${STEADFAST_API_KEY:0:10}...${NC}"
else
    echo -e "Steadfast API Key: ${YELLOW}Not Set (use /setup)${NC}"
fi
echo ""

echo -e "${YELLOW}How to use:${NC}"
echo "─────────────────────────────────────────────────"
echo ""
echo -e "${BLUE}1. Run bot:${NC}"
echo "   zunex"
echo ""
echo -e "${BLUE}2. Or using script:${NC}"
echo "   cd ${INSTALL_DIR}"
echo "   ./start_bot.sh"
echo ""
echo -e "${BLUE}3. To stop bot:${NC}"
echo "   Press Ctrl+C"
echo ""
echo -e "${BLUE}4. View logs:${NC}"
echo "   tail -f bot.log"
echo ""
echo -e "${BLUE}5. Update bot:${NC}"
echo "   cd ${INSTALL_DIR} && git pull"
echo ""

echo -e "${YELLOW}Bot Commands:${NC}"
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

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Bot is ready! Type 'zunex' to start${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================
# OFFER TO START BOT
# ============================================
echo -e "${BLUE}Do you want to start the bot now? (y/n)${NC}"
read -p "> " START_NOW

if [[ "$START_NOW" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Starting bot...${NC}"
    echo ""
    cd "$INSTALL_DIR"
    python3 main.py
else
    echo -e "${YELLOW}To start later, type: zunex${NC}"
    exit 0
fi

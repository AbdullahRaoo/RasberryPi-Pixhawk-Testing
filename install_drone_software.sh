#!/bin/bash
# Automated setup script for Raspberry Pi 4 + Pixhawk CubeBlack
# Repository: https://github.com/yourusername/rpi-pixhawk-setup
# Run with: bash install_drone_software.sh

set -e  # Exit on error
set -u  # Exit on undefined variable

# Script version
VERSION="1.0.0"

# Configuration
BAUDRATE=${BAUDRATE:-921600}
SERIAL_PORT=${SERIAL_PORT:-/dev/serial0}
INSTALL_VIDEO=${INSTALL_VIDEO:-yes}
INSTALL_MAVLINK_ROUTER=${INSTALL_MAVLINK_ROUTER:-no}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file
LOG_FILE="$HOME/drone_setup_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "======================================"
echo "Drone Companion Computer Setup v${VERSION}"
echo "Raspberry Pi 4 + Pixhawk CubeBlack"
echo "======================================"
echo ""
log "Installation started"

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}Please do not run as root (don't use sudo)${NC}"
    log "ERROR: Script run as root"
    exit 1
fi

# Check Raspberry Pi model
if [ -f /proc/device-tree/model ]; then
    RPI_MODEL=$(tr -d '\0' < /proc/device-tree/model)
    echo -e "${BLUE}Detected: $RPI_MODEL${NC}"
    log "Raspberry Pi model: $RPI_MODEL"
fi

# Check internet connectivity
echo "Checking internet connection..."
if ! ping -c 1 8.8.8.8 &> /dev/null; then
    echo -e "${RED}No internet connection detected!${NC}"
    echo "Please connect to the internet and try again."
    log "ERROR: No internet connection"
    exit 1
fi
echo -e "${GREEN}✓ Internet connected${NC}"
log "Internet connection verified"

echo -e "${GREEN}[1/8] Updating system packages...${NC}"
log "Updating system packages"
if ! sudo apt-get update >> "$LOG_FILE" 2>&1; then
    echo -e "${RED}Failed to update package lists${NC}"
    log "ERROR: apt-get update failed"
    exit 1
fi

echo "Upgrading packages (this may take several minutes)..."
if ! sudo apt-get upgrade -y >> "$LOG_FILE" 2>&1; then
    echo -e "${YELLOW}Warning: Some packages failed to upgrade${NC}"
    log "WARNING: apt-get upgrade had issues"
fi

echo -e "${GREEN}[2/8] Installing Python dependencies...${NC}"
log "Installing Python dependencies"
if ! sudo apt-get install -y python3-pip python3-dev python3-setuptools \
    build-essential git cmake >> "$LOG_FILE" 2>&1; then
    echo -e "${RED}Failed to install Python dependencies${NC}"
    log "ERROR: Python dependency installation failed"
    exit 1
fi

# Verify Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"
log "Python version: $PYTHON_VERSION"

echo -e "${GREEN}[3/8] Installing MAVProxy and PyMAVLink...${NC}"
log "Installing MAVProxy and PyMAVLink"

# Python 3.13+ requires --break-system-packages flag or virtual environment
PYTHON_VERSION_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_VERSION_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')
log "Python version: $PYTHON_VERSION_MAJOR.$PYTHON_VERSION_MINOR"

PIP_FLAGS="--upgrade"
if [ "$PYTHON_VERSION_MAJOR" -eq 3 ] && [ "$PYTHON_VERSION_MINOR" -ge 11 ]; then
    echo "Python 3.11+ detected, using --break-system-packages flag"
    PIP_FLAGS="--upgrade --break-system-packages"
    log "Using --break-system-packages for pip"
fi

# Install dependencies first (future module is required by MAVProxy)
echo "Installing MAVProxy dependencies..."
if ! sudo pip3 install $PIP_FLAGS future lxml 2>&1 | tee -a "$LOG_FILE"; then
    echo -e "${YELLOW}Warning: Some dependencies failed to install${NC}"
    log "WARNING: MAVProxy dependency installation had issues"
fi

# Install MAVProxy and PyMAVLink
if ! sudo pip3 install $PIP_FLAGS pymavlink MAVProxy 2>&1 | tee -a "$LOG_FILE"; then
    echo -e "${RED}Failed to install MAVProxy with pip${NC}"
    echo "Trying alternative installation method..."
    log "ERROR: MAVProxy pip installation failed, trying apt"
    
    # Try installing from apt as fallback
    if sudo apt-get install -y python3-pymavlink mavproxy >> "$LOG_FILE" 2>&1; then
        echo -e "${YELLOW}Installed MAVProxy from apt package${NC}"
        log "MAVProxy installed via apt"
    else
        echo -e "${RED}All installation methods failed${NC}"
        echo "Check log file: $LOG_FILE"
        log "ERROR: All MAVProxy installation methods failed"
        exit 1
    fi
fi

# Verify installation
if command -v mavproxy.py &> /dev/null; then
    MAVPROXY_VERSION=$(mavproxy.py --version 2>&1 | head -n 1 || echo "unknown")
    echo "MAVProxy installed: $MAVPROXY_VERSION"
    log "MAVProxy version: $MAVPROXY_VERSION"
else
    echo -e "${YELLOW}Warning: MAVProxy not found in PATH${NC}"
    log "WARNING: MAVProxy not in PATH"
fi

echo -e "${GREEN}[4/8] Installing DroneKit for Python scripting...${NC}"
log "Installing DroneKit"
if ! sudo pip3 install $PIP_FLAGS dronekit dronekit-sitl 2>&1 | tee -a "$LOG_FILE"; then
    echo -e "${YELLOW}Warning: DroneKit installation had issues${NC}"
    log "WARNING: DroneKit installation failed"
else
    echo "DroneKit installed successfully"
    log "DroneKit installed"
fi

echo -e "${GREEN}[5/8] Configuring UART for serial communication...${NC}"
log "Configuring UART"

# Determine config file location
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
else
    echo -e "${RED}Cannot find config.txt!${NC}"
    log "ERROR: config.txt not found"
    exit 1
fi

log "Using config file: $CONFIG_FILE"

# Disable Bluetooth on UART
if ! grep -q "dtoverlay=disable-bt" "$CONFIG_FILE"; then
    echo "dtoverlay=disable-bt" | sudo tee -a "$CONFIG_FILE" > /dev/null
    echo -e "${YELLOW}Added Bluetooth disable overlay${NC}"
    log "Added dtoverlay=disable-bt"
else
    echo "Bluetooth already disabled on UART"
    log "dtoverlay=disable-bt already present"
fi

# Disable Bluetooth service
if sudo systemctl disable hciuart 2>/dev/null; then
    log "Disabled hciuart service"
fi

# Add user to dialout group for serial access
if ! groups $USER | grep -q dialout; then
    sudo usermod -a -G dialout $USER
    echo -e "${YELLOW}Added $USER to dialout group${NC}"
    log "Added user to dialout group"
else
    echo "User already in dialout group"
    log "User already in dialout group"
fi

if [ "$INSTALL_VIDEO" = "yes" ]; then
    echo -e "${GREEN}[6/8] Installing video streaming tools...${NC}"
    log "Installing GStreamer"
    if ! sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-base \
        gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly >> "$LOG_FILE" 2>&1; then
        echo -e "${YELLOW}Warning: GStreamer installation had issues${NC}"
        log "WARNING: GStreamer installation failed"
    else
        echo "Video streaming tools installed"
        log "GStreamer installed"
    fi
else
    echo -e "${BLUE}[6/8] Skipping video streaming tools${NC}"
    log "Skipped video tools installation"
fi

echo -e "${GREEN}[7/8] Creating MAVProxy systemd service...${NC}"
log "Creating MAVProxy service"

# Find mavproxy.py location
MAVPROXY_PATH=$(which mavproxy.py || echo "/usr/local/bin/mavproxy.py")
log "MAVProxy path: $MAVPROXY_PATH"

sudo tee /etc/systemd/system/mavproxy.service > /dev/null <<EOF
[Unit]
Description=MAVProxy Telemetry Router
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
ExecStart=$MAVPROXY_PATH --master=$SERIAL_PORT --baudrate=$BAUDRATE --out=udp:0.0.0.0:14550 --daemon --state-basedir=/tmp/mavproxy
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
echo -e "${YELLOW}MAVProxy service created but not enabled${NC}"
log "MAVProxy service created"

echo -e "${GREEN}[8/8] Installing additional utilities...${NC}"
log "Installing utilities"
if ! sudo apt-get install -y screen htop vim >> "$LOG_FILE" 2>&1; then
    echo -e "${YELLOW}Warning: Some utilities failed to install${NC}"
    log "WARNING: Utility installation had issues"
fi

echo ""
echo -e "${GREEN}======================================"
echo "Installation Complete!"
echo -e "======================================${NC}"
echo ""
log "Installation completed successfully"

echo -e "${BLUE}Installation Summary:${NC}"
echo "  - Python: $PYTHON_VERSION"
echo "  - MAVProxy: Installed"
echo "  - DroneKit: Installed"
echo "  - Serial Port: $SERIAL_PORT"
echo "  - Baud Rate: $BAUDRATE"
echo "  - Log File: $LOG_FILE"
echo ""

echo -e "${YELLOW}⚠️  REQUIRED: Configure UART before first use!${NC}"
echo ""
echo "Step 1: Enable serial port"
echo "  sudo raspi-config"
echo "  → Interface Options → Serial Port"
echo "    • Login shell over serial: NO"
echo "    • Serial port hardware enabled: YES"
echo ""
echo -e "${YELLOW}Step 2: REBOOT your Raspberry Pi${NC}"
echo "  sudo reboot"
echo ""
echo "Step 3: Test connection after reboot"
echo "  cd ~/drone-setup  # or wherever you placed the files"
echo "  ./test_mavproxy.sh"
echo "  # or"
echo "  python3 test_connection.py"
echo ""
echo "Step 4: Enable auto-start (optional)"
echo "  sudo systemctl enable mavproxy.service"
echo "  sudo systemctl start mavproxy.service"
echo ""
echo -e "${BLUE}Your Raspberry Pi IP address:${NC}"
hostname -I | awk '{print "  " $1}'
echo ""
echo "Connect from Mission Planner/QGroundControl:"
echo "  Protocol: UDP"
echo "  Port: 14550"
echo ""
echo -e "${GREEN}📖 Read SETUP_GUIDE.md for detailed instructions${NC}"
echo -e "${GREEN}🔧 Read WIRING_GUIDE.md for hardware connections${NC}"
echo ""
log "Installation script finished"

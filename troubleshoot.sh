#!/bin/bash
# Troubleshooting script for Pixhawk connection issues
# Run with: bash troubleshoot.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Pixhawk Connection Troubleshooting"
echo "=========================================="
echo ""

# 1. Check serial port
echo -e "${BLUE}[1] Checking serial port...${NC}"
if [ -e /dev/serial0 ]; then
    echo -e "${GREEN}✓ /dev/serial0 exists${NC}"
    ls -l /dev/serial0
    ACTUAL_PORT=$(readlink -f /dev/serial0)
    echo "  Actual device: $ACTUAL_PORT"
else
    echo -e "${RED}✗ /dev/serial0 not found!${NC}"
    echo "  Run: sudo raspi-config"
    echo "  Interface Options → Serial Port"
    echo "    - Login shell: NO"
    echo "    - Hardware enabled: YES"
    exit 1
fi
echo ""

# 2. Check permissions
echo -e "${BLUE}[2] Checking permissions...${NC}"
if groups | grep -q dialout; then
    echo -e "${GREEN}✓ User is in dialout group${NC}"
else
    echo -e "${RED}✗ User NOT in dialout group${NC}"
    echo "  Run: sudo usermod -a -G dialout $USER"
    echo "  Then log out and back in"
fi
echo ""

# 3. Check if port is in use
echo -e "${BLUE}[3] Checking if port is in use...${NC}"
if lsof /dev/serial0 2>/dev/null; then
    echo -e "${YELLOW}⚠ Port is currently in use by another process${NC}"
    lsof /dev/serial0
    echo "  Kill the process with: sudo killall mavproxy.py"
else
    echo -e "${GREEN}✓ Port is available${NC}"
fi
echo ""

# 4. Check UART configuration
echo -e "${BLUE}[4] Checking UART configuration...${NC}"
if [ -f /boot/firmware/config.txt ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
elif [ -f /boot/config.txt ]; then
    CONFIG_FILE="/boot/config.txt"
else
    echo -e "${RED}✗ Cannot find config.txt${NC}"
    CONFIG_FILE=""
fi

if [ -n "$CONFIG_FILE" ]; then
    if grep -q "dtoverlay=disable-bt" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ Bluetooth disabled on UART${NC}"
    else
        echo -e "${YELLOW}⚠ Bluetooth NOT disabled on UART${NC}"
        echo "  Add to $CONFIG_FILE:"
        echo "  dtoverlay=disable-bt"
    fi
    
    if grep -q "enable_uart=1" "$CONFIG_FILE"; then
        echo -e "${GREEN}✓ UART explicitly enabled${NC}"
    else
        echo -e "${YELLOW}⚠ UART not explicitly enabled (may be okay)${NC}"
    fi
fi
echo ""

# 5. Test serial port with different baud rates
echo -e "${BLUE}[5] Testing serial communication...${NC}"
echo "Attempting to read from serial port for 3 seconds..."
echo "(This will show if ANY data is coming from Pixhawk)"
echo ""

for BAUD in 921600 57600 115200; do
    echo -e "${YELLOW}Testing at ${BAUD} baud...${NC}"
    timeout 3 stty -F /dev/serial0 $BAUD raw -echo
    if timeout 3 cat /dev/serial0 | head -c 100 > /tmp/serial_test_$BAUD 2>&1; then
        if [ -s /tmp/serial_test_$BAUD ]; then
            echo -e "${GREEN}✓ Data received at ${BAUD} baud!${NC}"
            echo "  First bytes: $(xxd -l 20 /tmp/serial_test_$BAUD | head -1)"
        else
            echo -e "${RED}✗ No data at ${BAUD} baud${NC}"
        fi
    else
        echo -e "${RED}✗ No data at ${BAUD} baud${NC}"
    fi
    rm -f /tmp/serial_test_$BAUD
done
echo ""

# 6. Check for ModemManager interference
echo -e "${BLUE}[6] Checking for ModemManager...${NC}"
if systemctl is-active --quiet ModemManager; then
    echo -e "${YELLOW}⚠ ModemManager is running (can interfere with serial)${NC}"
    echo "  To disable: sudo systemctl stop ModemManager"
    echo "  To disable permanently: sudo systemctl disable ModemManager"
else
    echo -e "${GREEN}✓ ModemManager is not running${NC}"
fi
echo ""

# 7. Hardware check reminder
echo -e "${BLUE}[7] Hardware Connection Checklist:${NC}"
echo "  Please verify the following connections:"
echo ""
echo "  CubeBlack TELEM2          Raspberry Pi 4"
echo "  ─────────────────────────────────────────"
echo "  Pin 2 (TX - Yellow)   →   GPIO 15 (RX, Pin 10)"
echo "  Pin 3 (RX - Green)    →   GPIO 14 (TX, Pin 8)"
echo "  Pin 6 (GND - Black)   →   GND (Pin 6)"
echo ""
echo -e "${RED}  ⚠ IMPORTANT: TX connects to RX, RX connects to TX${NC}"
echo -e "${RED}  ⚠ Do NOT connect +5V from Pixhawk to RPi${NC}"
echo ""

# 8. Flight controller configuration
echo -e "${BLUE}[8] Flight Controller Configuration:${NC}"
echo "  Connect to CubeBlack with Mission Planner and verify:"
echo ""
echo "  Parameter                 Required Value"
echo "  ────────────────────────────────────────"
echo "  SERIAL2_PROTOCOL          2 (MAVLink 2)"
echo "  SERIAL2_BAUD              921 (921600 baud)"
echo ""
echo "  Alternative (if TELEM2 doesn't work, try TELEM1):"
echo "  SERIAL1_PROTOCOL          2"
echo "  SERIAL1_BAUD              921"
echo ""

# 9. Suggested next steps
echo -e "${BLUE}[9] Suggested Next Steps:${NC}"
echo ""
if [ ! -e /dev/serial0 ]; then
    echo "  1. Enable UART in raspi-config and reboot"
elif ! groups | grep -q dialout; then
    echo "  1. Add user to dialout group and re-login"
else
    echo "  1. Verify physical wiring (TX↔RX, RX↔TX, GND↔GND)"
    echo "  2. Connect CubeBlack to Mission Planner"
    echo "  3. Check SERIAL2_PROTOCOL = 2 and SERIAL2_BAUD = 921"
    echo "  4. Ensure CubeBlack is powered and armed/disarmed"
    echo "  5. Try different TELEM port (TELEM1 instead of TELEM2)"
    echo "  6. Try lower baud rate: 57600"
    echo ""
    echo "  Test with lower baud rate:"
    echo "    mavproxy.py --master=/dev/serial0 --baudrate=57600"
fi
echo ""

echo "=========================================="
echo "Troubleshooting Complete"
echo "=========================================="

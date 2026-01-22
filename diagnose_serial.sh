#!/bin/bash
# diagnose_serial.sh - Troubleshoot RPi Serial Port Configuration

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}    Raspberry Pi Serial Diagnostic Tool   ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# 1. System Information
echo -e "${YELLOW}[1] System Information${NC}"
echo -e "Model: $(cat /proc/device-tree/model 2>/dev/null || echo "Unknown")"
echo -e "Kernel: $(uname -r)"
echo ""

# 2. Check /dev/serial entries
echo -e "${YELLOW}[2] Checking /dev/serial* links${NC}"
if ls -l /dev/serial* >/dev/null 2>&1; then
    ls -l /dev/serial*
else
    echo -e "${RED}✗ No /dev/serial* entries found!${NC}"
    echo -e "  This usually means UART is not enabled in proper mode."
fi
echo ""

# 3. Check physical UART devices
echo -e "${YELLOW}[3] Checking physical UART devices${NC}"
echo "Available ttyAMA/ttyS devices:"
ls -l /dev/ttyAMA* /dev/ttyS* 2>/dev/null | grep -E "ttyAMA|ttyS" | grep -v "ttyS[0-9][0-9]"
echo ""

# 4. Check Kernel Command Line (Console)
echo -e "${YELLOW}[4] Checking Kernel Command Line${NC}"
CMDLINE=$(cat /proc/cmdline)
echo "Current cmdline: $CMDLINE"
echo ""
if [[ "$CMDLINE" == *"console=serial0"* ]] || [[ "$CMDLINE" == *"console=ttyAMA0"* ]] || [[ "$CMDLINE" == *"console=ttyS0"* ]]; then
    echo -e "${RED}✗ Serial Console is ENABLED${NC}"
    echo -e "  The serial port is being used as a login shell."
    echo -e "  It cannot be used for Pixhawk telemetry while console is enabled."
    echo -e "  FIX: Run 'sudo raspi-config' -> Interface Options -> Serial Port"
    echo -e "       Login shell: NO, Hardware enabled: YES"
else
    echo -e "${GREEN}✓ Serial Console appears disabled (Good)${NC}"
fi
echo ""

# 5. Check Boot Config
echo -e "${YELLOW}[5] Checking Boot Config${NC}"
# Try to find config.txt
CONFIG_FILES=("/boot/config.txt" "/boot/firmware/config.txt")
FOUND_CONFIG=false

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "Found config at: $file"
        echo "----------------------------------------"
        grep -E "^enable_uart|^dtoverlay|^init_uart|^core_freq" "$file" || echo "No relevant settings found."
        echo "----------------------------------------"
        FOUND_CONFIG=true
    fi
done

if [ "$FOUND_CONFIG" = false ]; then
    echo -e "${RED}✗ Could not find config.txt${NC}"
else 
    echo -e "${BLUE}Tips:${NC}"
    echo -e "  - 'enable_uart=1' is required."
    echo -e "  - 'dtoverlay=disable-bt' is often recommended for PL011 on ttyAMA0."
fi
echo ""

# 6. Check User Permissions
echo -e "${YELLOW}[6] Checking User Permissions${NC}"
USER_GROUPS=$(groups)
if [[ "$USER_GROUPS" == *"dialout"* ]]; then
    echo -e "${GREEN}✓ User '$USER' is in 'dialout' group${NC}"
else
    echo -e "${RED}✗ User '$USER' is NOT in 'dialout' group${NC}"
    echo -e "  Fix: sudo usermod -a -G dialout $USER"
fi
echo ""

# 7. Hardware Test Suggestion
echo -e "${YELLOW}[7] Recommendations${NC}"
if [ ! -e /dev/serial0 ]; then
    echo -e "1. If /dev/ttyS0 exists, you can try using it directly."
    echo -e "2. Or enable UART properly in raspi-config."
else
    echo -e "1. Port /dev/serial0 exists. Use hardware_test.sh to test loopback or device."
fi

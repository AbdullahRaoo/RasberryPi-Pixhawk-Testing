#!/bin/bash
# Test different MAVProxy configurations
# Run with: bash test_all_configs.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "MAVProxy Configuration Tester"
echo "=========================================="
echo ""
echo "This will try different connection settings"
echo "Press Ctrl+C when you see heartbeat messages"
echo ""

# Configuration array: baudrate, flow_control_flag, description
# Starting with 57600 since that's the Mission Planner default
configs=(
    "57600:--rtscts:57600 with hardware flow control (RTS/CTS)"
    "57600::57600 without flow control"
    "115200:--rtscts:115200 with hardware flow control"
    "115200::115200 without flow control"
    "921600:--rtscts:921600 with hardware flow control"
    "921600::921600 without flow control"
)

for config in "${configs[@]}"; do
    IFS=':' read -r baud flow_flag desc <<< "$config"
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Testing: $desc${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "Command: mavproxy.py --master=/dev/serial0 --baudrate=$baud $flow_flag"
    echo ""
    echo "Waiting 10 seconds for connection..."
    echo "(If you see heartbeat messages, press Ctrl+C and use this configuration)"
    echo ""
    
    # Run MAVProxy with timeout
    timeout 10 mavproxy.py --master=/dev/serial0 --baudrate=$baud $flow_flag --aircraft MyCopter 2>&1 | head -30
    
    echo ""
    echo -e "${YELLOW}No heartbeat detected. Trying next configuration...${NC}"
    echo ""
    sleep 2
done

echo ""
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}No working configuration found!${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "Possible issues:"
echo "  1. CubeBlack SERIAL2_PROTOCOL not set to 2 (MAVLink 2)"
echo "  2. CubeBlack SERIAL2_BAUD doesn't match (should be 921, 115, or 57)"
echo "  3. Wrong TELEM port (try TELEM1 instead of TELEM2)"
echo "  4. Wiring issue (verify TX→RX, RX→TX, GND→GND)"
echo "  5. CubeBlack not powered or not booted"
echo ""
echo "Next steps:"
echo "  1. Run ./troubleshoot.sh for detailed diagnostics"
echo "  2. Connect CubeBlack to Mission Planner"
echo "  3. Verify SERIAL2_PROTOCOL=2 and SERIAL2_BAUD=921"
echo "  4. Check wiring with multimeter if available"

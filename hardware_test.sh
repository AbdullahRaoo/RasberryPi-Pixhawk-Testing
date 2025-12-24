#!/bin/bash
# Hardware diagnostic - check if ANY data is coming from CubeBlack
# Run with: bash hardware_test.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "Hardware Connection Diagnostic"
echo "=========================================="
echo ""

# Test 1: Check if serial port exists and is accessible
echo -e "${BLUE}[1] Checking serial port access...${NC}"
if [ -e /dev/serial0 ]; then
    echo -e "${GREEN}✓ /dev/serial0 exists${NC}"
    ls -l /dev/serial0
else
    echo -e "${RED}✗ /dev/serial0 not found${NC}"
    exit 1
fi
echo ""

# Test 2: Raw data test - does ANYTHING come through?
echo -e "${BLUE}[2] Testing for ANY incoming data...${NC}"
echo "Listening on serial port for 5 seconds..."
echo "** Make sure CubeBlack is POWERED ON **"
echo ""

for BAUD in 57600 115200 921600; do
    echo -e "${YELLOW}Testing at $BAUD baud...${NC}"
    
    # Configure serial port
    stty -F /dev/serial0 $BAUD raw -echo -echoe -echok 2>/dev/null
    
    # Try to read any data for 3 seconds
    timeout 3 cat /dev/serial0 > /tmp/serial_raw_$BAUD 2>&1 &
    PID=$!
    
    # Show spinner while waiting
    for i in {1..3}; do
        echo -n "."
        sleep 1
    done
    wait $PID 2>/dev/null
    echo ""
    
    # Check if any data was received
    if [ -s /tmp/serial_raw_$BAUD ]; then
        SIZE=$(wc -c < /tmp/serial_raw_$BAUD)
        echo -e "${GREEN}✓ RECEIVED $SIZE bytes at $BAUD baud!${NC}"
        echo "First 50 bytes (hex):"
        xxd -l 50 /tmp/serial_raw_$BAUD
        echo ""
        echo -e "${GREEN}SUCCESS! Data is being received.${NC}"
        echo "This means wiring is likely correct."
        echo ""
        rm -f /tmp/serial_raw_*
        
        # Now try MAVLink detection
        echo -e "${BLUE}[3] Checking if it's valid MAVLink data...${NC}"
        echo "Looking for MAVLink magic bytes (FD, FE)..."
        
        timeout 5 cat /dev/serial0 | xxd | head -20
        
        echo ""
        echo -e "${YELLOW}If you see 'FD' or 'FE' bytes above, it's MAVLink!${NC}"
        echo ""
        echo "Recommended next steps:"
        echo "  1. Your wiring appears correct"
        echo "  2. Use MAVProxy at $BAUD baud:"
        echo "     mavproxy.py --master=/dev/serial0 --baudrate=$BAUD --rtscts"
        echo ""
        exit 0
    else
        echo -e "${RED}✗ No data at $BAUD baud${NC}"
    fi
    
    rm -f /tmp/serial_raw_$BAUD
    echo ""
done

# If we got here, no data at any baud rate
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${RED}NO DATA RECEIVED AT ANY BAUD RATE${NC}"
echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}This indicates a hardware issue:${NC}"
echo ""
echo "1. Is the CubeBlack POWERED ON?"
echo "   - Check if the CubeBlack has lights"
echo "   - Connect USB to CubeBlack to power it"
echo ""
echo "2. Check your wiring:"
echo "   CubeBlack TELEM2          Raspberry Pi"
echo "   ──────────────────────────────────────"
echo "   Pin 2 (TX - Yellow)   →   Pin 10 (GPIO 15 - RX)"
echo "   Pin 3 (RX - Green)    →   Pin 8  (GPIO 14 - TX)"
echo "   Pin 6 (GND - Black)   →   Pin 6  (GND)"
echo ""
echo "3. CRITICAL: TX goes to RX, RX goes to TX"
echo "   - CubeBlack TX → Raspberry Pi RX"
echo "   - CubeBlack RX → Raspberry Pi TX"
echo ""
echo "4. Try connecting to TELEM1 instead of TELEM2"
echo "   (Then set SERIAL1_PROTOCOL=2 in Mission Planner)"
echo ""
echo "5. Use a multimeter to check:"
echo "   - GND continuity between CubeBlack and RPi"
echo "   - Voltage on TX pin (should be ~3.3V when transmitting)"
echo ""
echo "6. In Mission Planner, verify:"
echo "   - SERIAL2_PROTOCOL = 2"
echo "   - SERIAL2_BAUD = 57 (or 115 or 921)"
echo "   - Parameters are saved and CubeBlack rebooted"
echo ""

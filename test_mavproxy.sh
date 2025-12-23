#!/bin/bash
# Quick test script for MAVProxy connection
# Run with: bash test_mavproxy.sh

echo "======================================"
echo "MAVProxy Connection Test"
echo "======================================"
echo ""

# Check if serial0 exists
if [ ! -e /dev/serial0 ]; then
    echo "ERROR: /dev/serial0 not found!"
    echo "Have you enabled UART in raspi-config?"
    echo ""
    echo "Run: sudo raspi-config"
    echo "Then: Interface Options -> Serial Port"
    echo "  - Login shell: NO"
    echo "  - Hardware enabled: YES"
    exit 1
fi

# Check permissions
if ! groups | grep -q dialout; then
    echo "WARNING: You are not in the dialout group"
    echo "Run: sudo usermod -a -G dialout $USER"
    echo "Then log out and back in"
    echo ""
fi

echo "Serial port found: /dev/serial0"
ls -l /dev/serial0
echo ""

echo "Starting MAVProxy..."
echo "If connection is successful, you should see heartbeat messages"
echo ""
echo "Test commands to try:"
echo "  param show ARMING_CHECK"
echo "  mode GUIDED"
echo "  status"
echo ""
echo "Press Ctrl+C to exit"
echo ""

# Start MAVProxy with common settings
mavproxy.py --master=/dev/serial0 --baudrate=921600 --aircraft MyCopter

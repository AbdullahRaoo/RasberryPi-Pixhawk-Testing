#!/bin/bash
# Quick connection test at 57600 baud (Mission Planner default)
# Run with: bash quick_test.sh

echo "Quick Connection Test - 57600 baud"
echo "===================================="
echo ""

# Stop ModemManager if running
if systemctl is-active --quiet ModemManager; then
    echo "Stopping ModemManager (it can interfere)..."
    sudo systemctl stop ModemManager
    echo ""
fi

echo "Connecting at 57600 baud with hardware flow control..."
echo "Press Ctrl+C to exit"
echo ""
echo "If you see 'Received N packets', connection is working!"
echo ""

mavproxy.py --master=/dev/serial0 --baudrate=57600 --rtscts

#!/usr/bin/env python3
"""
Simple Serial Loopback Test
---------------------------
Tests the Raspberry Pi UART by sending data out and expecting it back.

INSTRUCTIONS:
1. Disconnect the Pixhawk.
2. Connect a jumper wire directly between Pin 8 (TX) and Pin 10 (RX) on the Raspberry Pi.
3. Run this script: python3 simple_loopback.py
"""

import serial
import time
import sys

# Try to find the correct port
PORT = '/dev/serial0'
BAUD = 57600

def test_loopback():
    print("=" * 40)
    print("Serial Loopback Test")
    print("=" * 40)
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print("-" * 40)
    print("INSTRUCTIONS:")
    print("1. Connect a wire from Pin 8 (TX) to Pin 10 (RX).")
    print("2. Disconnect any other devices ( Pixhawk ).")
    print("-" * 40)
    
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("✓ Port opened successfully")
    except Exception as e:
        print(f"✗ Failed to open port: {e}")
        # Try ttyS0 fallback
        try:
            print("Trying /dev/ttyS0 instead...")
            ser = serial.Serial("/dev/ttyS0", BAUD, timeout=1)
            print("✓ /dev/ttyS0 opened successfully")
        except:
            print("✗ Could not open /dev/serial0 or /dev/ttyS0")
            return False

    # Clear buffer
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print("\nStarting Test...")
    
    # Test Data
    test_message = b"Hello Raspberry Pi UART!"
    
    # Write
    print(f"Sending: {test_message}")
    ser.write(test_message)
    
    # Read
    time.sleep(0.1)
    received = ser.read(len(test_message))
    
    print(f"Received: {received}")
    
    print("-" * 40)
    if received == test_message:
        print("✓ SUCCESS: Loopback confirmed!")
        print("  Your Raspberry Pi UART is working correctly.")
        print("  The issue is likely the WIRING or the PIXHAWK config.")
    else:
        print("✗ FAILURE: Data did not match.")
        if len(received) == 0:
            print("  No data received. check your jumper wire connection.")
        else:
            print("  Data corrupted.")
            
    ser.close()
    return True

if __name__ == "__main__":
    test_loopback()

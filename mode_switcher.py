#!/usr/bin/env python3
"""
Mode Switcher Test
------------------
Demonstrates sending commands to the drone.
SAFE: Only changes Flight Mode. Does NOT arm motors.
"""

import collections
import collections.abc
# Monkey patch for Python 3.10+ compatibility with DroneKit
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode
import time
import sys

# Connection Config
CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def main():
    print("Connecting to Pixhawk... (Please Wait)")
    try:
        vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
        print("✓ Connected!")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return

    print("Current Mode: %s" % vehicle.mode.name)
    print("-" * 30)
    print("Test 1: Switching to GUIDED")
    vehicle.mode = VehicleMode("GUIDED")
    
    # Wait for mode change
    while vehicle.mode.name != 'GUIDED':
        print(" Waiting for mode change...")
        time.sleep(1)
    print("✓ Mode is now GUIDED")
    
    time.sleep(2)
    
    print("-" * 30)
    print("Test 2: Switching back to STABILIZE")
    vehicle.mode = VehicleMode("STABILIZE")
    
    while vehicle.mode.name != 'STABILIZE':
        print(" Waiting for mode change...")
        time.sleep(1)
    print("✓ Mode is now STABILIZE")
    
    print("-" * 30)
    print("Test Complete. Closing.")
    vehicle.close()

if __name__ == "__main__":
    main()

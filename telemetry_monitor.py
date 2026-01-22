#!/usr/bin/env python3
"""
Safe Indoor Telemetry Monitor
-----------------------------
Connects to the Pixhawk and prints vital data in real-time.
SAFE FOR INDOOR USE: Does NOT arm the motors.
"""

import collections
import collections.abc
# Monkey patch for Python 3.10+ compatibility with DroneKit
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect
import time
import sys
import os

# Connection Config
CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def clear_screen():
    os.system('clear')

def main():
    print("Connecting to Pixhawk... (Please Wait)")
    
    try:
        vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
        print("✓ Connected!")
        time.sleep(1)
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return

    print("Starting Telemetry Monitor... (Ctrl+C to stop)")
    time.sleep(2)

    try:
        while True:
            # Gather Data
            att = vehicle.attitude
            batt = vehicle.battery
            gps = vehicle.gps_0
            mode = vehicle.mode.name
            armed = vehicle.armed
            
            # Formatting Data
            # Pitch/Roll in degrees
            pitch_deg = att.pitch * 57.2958
            roll_deg = att.roll * 57.2958
            yaw_deg = att.yaw * 57.2958
            
            # Display
            clear_screen()
            print("="*40)
            print("       DRONE TELEMETRY MONITOR")
            print("="*40)
            print(f" STATUS:  {'ARMED ⚠️' if armed else 'DISARMED (Safe)'}")
            print(f" MODE:    {mode}")
            print("-" * 40)
            print(" ATTITUDE:")
            print(f"   Pitch: {pitch_deg:6.1f}°")
            print(f"   Roll:  {roll_deg:6.1f}°")
            print(f"   Yaw:   {yaw_deg:6.1f}°")
            print("-" * 40)
            print(" SENSORS:")
            print(f"   Voltage: {batt.voltage} V")
            print(f"   GPS Fix: {gps.fix_type} (Sats: {gps.satellites_visible})")
            print(f"   Alt:     {vehicle.location.global_relative_frame.alt:.2f} m")
            print("="*40)
            print("Move the drone around to see values change!")
            print("Press Ctrl+C to Exit")
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nStopping...")
        vehicle.close()
        print("Done.")

if __name__ == "__main__":
    main()

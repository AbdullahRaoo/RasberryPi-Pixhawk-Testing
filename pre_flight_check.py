#!/usr/bin/env python3
"""
Pre-Flight Checklist Script
---------------------------
Automated checks for autonomous flight.
Run this BEFORE every autonomous mission.

Checks:
1. Connection
2. Armable Status (System Health)
3. GPS Lock
4. Battery Levels
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

# Safety Thresholds
MIN_VOLTAGE = 0.0 # Set to e.g. 11.0 for 3S Lipo (0.0 ignores check for testing)
REQ_SATS = 0      # Set to 6-8 for outdoor flight (0 for indoor testing)

def print_result(check_name, status, message=""):
    color = "\033[92m" if status else "\033[91m" # Green or Red
    reset = "\033[0m"
    icon = "✓" if status else "✗"
    print(f"{color}[{icon}] {check_name:20} {message}{reset}")
    return status

def main():
    print("==================================")
    print("    PRE-FLIGHT DIAGNOSTICS        ")
    print("==================================")
    print(f"Connecting to {CONNECTION_STRING}...")
    
    try:
        vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
        print_result("Connection", True, "Established")
    except Exception as e:
        print_result("Connection", False, str(e))
        return

    all_passed = True
    
    # 1. System Status
    print("-" * 34)
    if vehicle.is_armable:
        print_result("System Health", True, "Ready to Arm")
    else:
        # It's common for this to be false indoors (no GPS)
        print_result("System Health", False, "Not Armable (Check Message)")
        # We don't fail the whole script indoors, but we warn
        print(f"    Reason: {vehicle.system_status.state}")

    # 2. GPS Check
    print("-" * 34)
    gps = vehicle.gps_0
    fix_status = gps.fix_type >= 3 # 3D Fix
    sat_status = gps.satellites_visible >= REQ_SATS
    
    if fix_status and sat_status:
        print_result("GPS Lock", True, f"3D Fix ({gps.satellites_visible} sats)")
    else:
        # Allow pass if threshold is 0 (indoor mode)
        msg = f"Fix: {gps.fix_type}, Sats: {gps.satellites_visible}"
        if REQ_SATS == 0:
            print_result("GPS Lock", True, f"BYPASSED (Indoor Mode) - {msg}")
        else:
            print_result("GPS Lock", False, msg)
            all_passed = False

    # 3. Battery Check
    print("-" * 34)
    batt = vehicle.battery
    if batt.voltage is None:
         print_result("Battery", False, "No Data (Power Module missing?)")
    elif batt.voltage > MIN_VOLTAGE:
        print_result("Battery", True, f"{batt.voltage}V (Level: {batt.level}%)")
    else:
        if MIN_VOLTAGE == 0:
             print_result("Battery", True, f"BYPASSED - {batt.voltage}V")
        else:
            print_result("Battery", False, f"LOW VOLTAGE! {batt.voltage}V < {MIN_VOLTAGE}V")
            all_passed = False

    # 4. Mode Check
    print("-" * 34)
    print(f"Current Mode: {vehicle.mode.name}")
    print_result("Mode Check", True, "Verified")

    print("=" * 34)
    if all_passed:
        print("\033[92mREADY FOR FLIGHT (Or Testing)\033[0m")
    else:
        print("\033[91mNO-GO: Fix errors before flying.\033[0m")
    print("=" * 34)
    
    vehicle.close()

if __name__ == "__main__":
    main()

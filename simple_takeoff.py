#!/usr/bin/env python3
"""
SIMPLE TAKEOFF & LAND
---------------------
1. Arm
2. Takeoff to 3m
3. Hover 2s
4. Land

REQ: Outdoor GPS Lock.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode
import time

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def main():
    print("Connecting... (Timeout 120s)")
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE, timeout=120)
    print("✓ Connected")

    # PRE-FLIGHT CHECKS
    if vehicle.gps_0.fix_type < 3:
        print("✗ NO GPS FIX!")
        return

    print("\n" + "="*40)
    print("      SIMPLE MISSION: UP -> WAIT -> DOWN")
    print("      Waiting for GUIDED switch...")
    print("="*40)
    
    while vehicle.mode.name != 'GUIDED':
        time.sleep(0.5)
        print(f"\rCurrent: {vehicle.mode.name}", end="")
    
    print("\n\n>>> LAUNCHING <<<")
    
    try:
        # ARM
        print("Arming...")
        vehicle.armed = True
        while not vehicle.armed: time.sleep(1)
        
        # TAKEOFF
        target_alt = 3
        print(f"Taking off to {target_alt}m...")
        vehicle.simple_takeoff(target_alt)
        
        while True:
            alt = vehicle.location.global_relative_frame.alt
            print(f" Altitude: {alt:.1f}m")
            if alt >= target_alt * 0.95: # 95% of target
                print(" Reached Target Altitude")
                break
            
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)

        # HOVER
        print("Hovering for 2 seconds...")
        time.sleep(2)

        # LAND
        print("Landing...")
        vehicle.mode = VehicleMode("LAND")
        while vehicle.armed:
            print(f" Descending... {vehicle.location.global_relative_frame.alt:.1f}m")
            time.sleep(1)
            
        print("✓ TOUCHDOWN")

    except Exception as e:
        print(f"\nABORTED: {e}")

    vehicle.close()

if __name__ == "__main__":
    main()

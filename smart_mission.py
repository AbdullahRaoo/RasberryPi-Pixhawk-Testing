#!/usr/bin/env python3
"""
Smart Mission (Safety Override Demo)
------------------------------------
INDUSTRY STANDARD WORKFLOW:
1. Pilot flies manually (Stabilize/Loiter).
2. Pilot switches to GUIDED -> Code detects this and starts mission.
3. Pilot switches OUT of GUIDED -> Code detects override and aborts.

SAFE FOR INDOORS: Does not arm or spin motors.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode
import time
import sys

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def main():
    print("Connecting to Pixhawk...")
    try:
        vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
        print("✓ Connected")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return

    print("\n" + "="*50)
    print("      SMART MISSION CONTROLLER")
    print("      Waiting for Pilot to engage GUIDED mode...")
    print("="*50)
    
    # 1. WAIT FOR PILOT TO ENGAGE GUIDED
    while vehicle.mode.name != 'GUIDED':
        print(f"\rCurrent Mode: {vehicle.mode.name} (Waiting for GUIDED...)", end="")
        time.sleep(0.5)
    
    print("\n\n>>> GUIDED MODE DETECTED: MISSION STARTING! <<<")
    
    # 2. RUN MISSION (With constant safety checks)
    try:
        for i in range(1, 101):
            # CONSTANT SAFETY CHECK (The "Hearthbeat" of the mission)
            if vehicle.mode.name != 'GUIDED':
                print(f"\n\n!!! SAFETY OVERRIDE DETECTED !!!")
                print(f"Pilot switched to {vehicle.mode.name}.")
                print("ABORTING MISSION IMMEDIATELY.")
                return

            # Simulate doing work
            print(f"\r[ Mission Running: {i}% completed ]", end="")
            
            # Pretend to fly to waypoints
            if i == 20: print("\n   -> Reached Waypoint 1")
            if i == 50: print("\n   -> Reached Waypoint 2")
            if i == 80: print("\n   -> Reached Waypoint 3")
            
            time.sleep(0.1) # Simulate flight time
            
        print("\n\n>>> MISSION COMPLETE <<<")
        print("Switch back to STABILIZE to land/disarm manually.")
        
    except KeyboardInterrupt:
        print("\nForce Quit.")

    vehicle.close()

if __name__ == "__main__":
    main()

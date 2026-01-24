#!/usr/bin/env python3
"""
Smart Mission (INDOOR VERSION)
------------------------------
Standard GUIDED mode requires GPS. We don't have it indoors.
This script demonstrates the "Trigger" logic using STABILIZE mode.

1. Wait for pilot to switch to ALT_HOLD (Trigger).
2. Script takes over -> Switches to STABILIZE.
3. Script ARMS motors.
4. Script Runs Motors at Idle for 5 seconds.
5. Script DISARMS.

SAFETY: PROPS MUST BE OFF.
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
    print("Connecting... (This may take up to 2 minutes)")
    # Increased timeout to 120s to handle slow parameter download
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE, timeout=120)
    print("✓ Connected")

    print("\n" + "="*50)
    print("      INDOOR MISSION DEMO")
    print("      PROPS MUST BE REMOVED!")
    print("      Waiting for you to switch to ALT_HOLD...")
    print("      (This is our 'Start Button')")
    print("="*50)
    
    # 1. WAIT FOR TRIGGER (AltHold)
    # We use AltHold as the "I'm ready" signal because it's distinct from Stabilize
    while vehicle.mode.name != 'ALT_HOLD':
        time.sleep(0.5)
        print(f"\rWaiting... Current: {vehicle.mode.name}", end="")
    
    print("\n\n>>> TRIGGER RECEIVED! STARTING SEQUENCE <<<")

    try:
        # 2. SWITCH TO STABILIZE (For safe indoor arming without GPS)
        print("Switching to STABILIZE (Indoor Safe Mode)...")
        vehicle.mode = VehicleMode("STABILIZE")
        time.sleep(1)

        # 3. ARMING
        if not vehicle.armed:
            print("Arming Motors (Watch out!)...")
            vehicle.armed = True
            
            # Wait for arming
            start = time.time()
            while not vehicle.armed:
                print(" Waiting to Arm...", end="\r")
                time.sleep(1)
                if time.time() - start > 10:
                    print("\n✗ Failed to Arm (Check Pre-Arms?)")
                    return
        print("\n✓ ARMED - IDLING")

        # 4. "MISSION" (Just Idling to prove control)
        print("Running Mission: Idle for 5 seconds...")
        for i in range(5, 0, -1):
            print(f" {i}...")
            # Safety Check: If user switches mode, abort
            if vehicle.mode.name != 'STABILIZE':
                 print("\nOVERRIDE DETECTED!")
                 return
            time.sleep(1)

        # 5. DISARM
        print("Mission Complete. Disarming...")
        vehicle.armed = False
        while vehicle.armed:
            time.sleep(1)
            
        print("✓ DISARMED. SUCCESS.")

    except Exception as e:
        print(f"\n\n!!! ERROR: {e} !!!")
        vehicle.armed = False

    vehicle.close()

if __name__ == "__main__":
    main()

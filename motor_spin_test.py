#!/usr/bin/env python3
"""
Safe Motor Spin Test
--------------------
Uses MAV_CMD_DO_MOTOR_TEST to spin motors one by one.
Safest way to verify wiring order.
PROPS MUST BE REMOVED.
BATTERY MUST BE CONNECTED (USB is not enough).
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, Command, VehicleMode
from pymavlink import mavutil
import time

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def spin_motor(vehicle, motor_num, duration_sec=1, throttle_pct=5):
    """
    Spins a specific motor using MAV_CMD_DO_MOTOR_TEST
    motor_num: 1-4 (Standard ArduCopter order)
    """
    print(f"   >>> Spinning Motor {motor_num} at {throttle_pct}% for {duration_sec}s...")
    
    # MAV_CMD_DO_MOTOR_TEST (209)
    # param1: Motor instance number (1-based)
    # param2: Throttle type (0=Throttle percentage, 1=PWM, 2=Pilot throttle, 3=Pass-through)
    # param3: Throttle (0-100%)
    # param4: Timeout (seconds)
    # param5: Motor count (0 for single motor)
    
    msg = vehicle.message_factory.command_long_encode(
        0, 0,    # target_system, target_component
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST, # command
        0,       # confirmation
        motor_num, # param1 (Motor identification)
        0,       # param2 (Throttle type 0=percent)
        throttle_pct, # param3 (Throttle %)
        duration_sec, # param4 (Timeout)
        1,       # param5 (Motor count) - leave as 0 or 1
        0, 0     # param6, param7
    )
    vehicle.send_mavlink(msg)
    time.sleep(duration_sec + 0.5)

def main():
    print("="*40)
    print("      MOTOR TEST SEQUENCE")
    print("      (PROPS MUST BE OFF)")
    print("="*40)
    
    print("Connecting...")
    try:
        vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
        print("✓ Connected")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return

    # Check for battery voltage - rough check for LiPo
    if vehicle.battery.voltage is None or vehicle.battery.voltage < 5:
        print("!"*40)
        print("WARNING: Voltage is basically 0.")
        print("Motors can NOT spin on USB power.")
        print("Please connect the Main Battery.")
        print("!"*40)
        input("Press ENTER if you have connected the battery (or to try anyway)...")

    # Safety Lock
    print("\nSAFETY CONFIRMATION:")
    response = input("Are PROPELLERS REMOVED? (yes/no): ")
    if response.lower() != "yes":
        print("Aborting for safety.")
        return

    print("\nStarting Test - Keep hands clear!")
    time.sleep(1)

    # Standard X-Quad Motor Order:
    # 1: Front Right (CCW)
    # 2: Rear Left   (CCW)
    # 3: Front Left  (CW)
    # 4: Rear Right  (CW)
    
    for i in range(1, 5):
        print(f"\n[?] Testing Motor {i}")
        spin_motor(vehicle, i, duration_sec=2, throttle_pct=5)
        
    print("\nDone. If any motor didn't spin:")
    print("1. Check ESC Signal wiring.")
    print("2. Check Battery connection.")
    print("3. Ensure Safety Switch (if equipped) is pressed.")

    vehicle.close()

if __name__ == "__main__":
    main()

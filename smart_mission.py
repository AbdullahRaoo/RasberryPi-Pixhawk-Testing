#!/usr/bin/env python3
"""
Smart Mission (REAL COMMANDS)
-----------------------------
1. Waits for pilot to switch to GUIDED.
2. ARMS motors.
3. TAKES OFF to 4 meters.
4. MOVES FORWARD 4 meters.
5. LANDS.

SAFETY: PROPS MUST BE OFF.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not used)

    # send command to vehicle on 1 Hz cycle
    for x in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

def main():
    print("Connecting...")
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
    print("✓ Connected")

    print("\n" + "="*50)
    print("      REAL MISSION CONTROLLER")
    print("      PROPS MUST BE REMOVED!")
    print("      Waiting for GUIDED mode...")
    print("="*50)
    
    # 1. WAIT FOR GUIDED
    while vehicle.mode.name != 'GUIDED':
        time.sleep(1)
        print(f"\rWaiting for switch... (Current: {vehicle.mode.name})", end="")
    
    print("\n\n>>> GUIDED DETECTED. STARTING MISSION <<<")

    try:
        # 2. ARMING
        if not vehicle.armed:
            print("Arms Motors...")
            vehicle.armed = True
            while not vehicle.armed:
                print(" Waiting for arming...")
                time.sleep(1)
                if vehicle.mode.name != 'GUIDED': raise Exception("Safety Switch Triggered")
        print("✓ ARMED")

        # 3. TAKEOFF
        print("Taking off to 4 meters...")
        vehicle.simple_takeoff(4)
        
        # Wait for climb (approx check)
        # Note: Indoors, altitude reading might be garbage (barometer drift)
        for i in range(10): 
            print(f" Altitude: {vehicle.location.global_relative_frame.alt:.1f}m")
            time.sleep(1)
            if vehicle.mode.name != 'GUIDED': raise Exception("Safety Switch Triggered")

        # 4. MOVE FORWARD (North)
        # 4 meters forward. Let's fly at 1 m/s for 4 seconds.
        print("Moving Forward (North) at 1m/s for 4s...")
        send_ned_velocity(vehicle, 1, 0, 0, 4)

        # 5. LAND
        print("Landing...")
        vehicle.mode = VehicleMode("LAND")
        while vehicle.armed:
            print(f" Descending... Alt: {vehicle.location.global_relative_frame.alt:.1f}m")
            time.sleep(1)
            
        print("✓ MISSION COMPLETE. DISARMED.")

    except Exception as e:
        print(f"\n\n!!! ABORTED: {e} !!!")
        vehicle.mode = VehicleMode("STABILIZE")

    vehicle.close()

if __name__ == "__main__":
    main()

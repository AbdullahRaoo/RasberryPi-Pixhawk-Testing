#!/usr/bin/env python3
"""
LINEAR MISSION (Point A to Point B)
-----------------------------------
1. Arm
2. Takeoff to 5m
3. Fly 10m North
4. Land at Destination (Do not RTL)

REQ: Outdoor GPS Lock.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def get_location_metres(original_location, dNorth, dEast):
    earth_radius = 6378137.0 
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobalRelative(newlat, newlon, original_location.alt)

def main():
    print("Connecting to Pixhawk... (Timeout 120s)")
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE, timeout=120)
    print("✓ Connected")

    # PRE-FLIGHT CHECKS
    if vehicle.gps_0.fix_type < 3:
        print("✗ NO GPS FIX!")
        return

    print("\n" + "="*40)
    print("      LINEAR MISSION: 5m UP -> 10m NORTH -> LAND")
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
        print("Taking off to 5 meters...")
        vehicle.simple_takeoff(5)
        
        while True:
            alt = vehicle.location.global_relative_frame.alt
            print(f" Altitude: {alt:.1f}m")
            if alt >= 4.8: break
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)

        # FLY 10M NORTH
        print("\nFlying 10m North...")
        # Get target location: Current Lat/Lon + 10m North + 0m East
        target = get_location_metres(vehicle.location.global_relative_frame, 10, 0)
        vehicle.simple_goto(target)
        
        # Wait for travel (approx 10s at 1m/s)
        for i in range(10):
            print(f" Traveling... {10-i}s remaining")
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)

        # LAND AT DESTINATION
        print("\nDestination Reached. Landing...")
        vehicle.mode = VehicleMode("LAND")
        while vehicle.armed:
            print(f" Descending... {vehicle.location.global_relative_frame.alt:.1f}m")
            time.sleep(1)
            
        print("✓ MISSION COMPLETE")

    except Exception as e:
        print(f"\nABORTED: {e}")

    vehicle.close()

if __name__ == "__main__":
    main()

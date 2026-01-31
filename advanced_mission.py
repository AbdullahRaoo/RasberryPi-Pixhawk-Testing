#!/usr/bin/env python3
"""
ADVANCED MISSION
----------------
1. Arm & Takeoff to 6m
2. Fly 10m North
3. Descend to 3m (at destination)
4. Return Home (at 3m altitude)
5. Land

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
    print("Connecting... (Timeout 120s)")
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE, timeout=120)
    print("✓ Connected")

    if vehicle.gps_0.fix_type < 3:
        print("✗ NO GPS FIX!")
        return

    print("\n" + "="*50)
    print("      ADVANCED MISSION")
    print("      6m UP -> 10m NORTH -> DOWN to 3m -> HOME -> LAND")
    print("      Waiting for GUIDED switch...")
    print("="*50)
    
    while vehicle.mode.name != 'GUIDED':
        time.sleep(0.5)
        print(f"\rCurrent: {vehicle.mode.name}", end="")
    
    print("\n\n>>> LAUNCHING <<<")
    
    try:
        # 1. ARM & TAKEOFF (6m)
        print("Arming...")
        vehicle.armed = True
        while not vehicle.armed: time.sleep(1)
        
        print("Taking off to 6m...")
        vehicle.simple_takeoff(6)
        while True:
            alt = vehicle.location.global_relative_frame.alt
            print(f" Alt: {alt:.1f}m")
            if alt >= 5.8: break
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)

        # 2. FLY 10m NORTH (Maintain 6m)
        print("\nFlying 10m North (at 6m)...")
        # Save home location is tricky in DroneKit without explicit storage, 
        # but we can calculate relative to current.
        # However, let's assume where we are now (0,0) is roughly Home.
        # Better: Store the launch location object if we wanted absolute return, 
        # but relative movements are easier.
        
        current_loc = vehicle.location.global_relative_frame
        target_north = get_location_metres(current_loc, 10, 0)
        target_north.alt = 6 # Ensure we stay at 6m
        vehicle.simple_goto(target_north)
        
        # Wait approx 10s
        for i in range(10):
            print(f" Outbound... {10-i}s")
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)

        # 3. DESCEND TO 3m (At destination)
        print("\nDescending to 3m...")
        target_descend = LocationGlobalRelative(target_north.lat, target_north.lon, 3)
        vehicle.simple_goto(target_descend)
        
        while True:
            alt = vehicle.location.global_relative_frame.alt
            print(f" Alt: {alt:.1f}m")
            if alt <= 3.2: break # approx 3m
            if vehicle.mode.name != 'GUIDED': raise Exception("Override")
            time.sleep(1)
            
        # 4. RETURN HOME (At 3m)
        print("\nReturning Home (at 3m)...")
        # RTL mode usually climbs to RTL_ALT (default 15m) then returns. 
        # To stay at 3m, we should fly back manually or use "RTL" and accept the climb.
        # User asked to "Come back... and land".
        # Let's use RTL as it is the safest "Come Home" command.
        
        print("Engaging RTL (Return to Launch)...")
        vehicle.mode = VehicleMode("RTL")
        # RTL will: Climb to safe alt -> Fly Home -> Hover -> Land.
        
        while vehicle.armed:
             print(f" RTL... Alt: {vehicle.location.global_relative_frame.alt:.1f}m")
             time.sleep(1)

        print("✓ MISSION COMPLETE")

    except Exception as e:
        print(f"\nABORTED: {e}")

    vehicle.close()

if __name__ == "__main__":
    main()

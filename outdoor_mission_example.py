#!/usr/bin/env python3
"""
OUTDOOR MISSION EXAMPLE (The "Proper" Way)
------------------------------------------
This script demonstrates a full autonomous mission.
REQUIREMENTS:
1. OUTDOORS (Clear view of sky)
2. GPS LOCK (3D Fix, Blue/Green LED)
3. PROPS ON (Ready to fly)

WORKFLOW:
1. Connect
2. Wait for Pilot to switch to GUIDED
3. Arm
4. Takeoff to 5m
5. Fly to a Square pattern
6. Return to Launch (RTL)
"""

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

CONNECTION_STRING = '/dev/serial0'
BAUD_RATE = 57600

def get_location_metres(original_location, dNorth, dEast):
    """
    Returns a LocationGlobalRelative object containing the latitude/longitude `dNorth` and `dEast` metres from the 
    specified `original_location`.
    """
    earth_radius = 6378137.0 #Radius of "spherical" earth
    #Coordinate offsets in radians
    dLat = dNorth/earth_radius
    dLon = dEast/(earth_radius*math.cos(math.pi*original_location.lat/180))

    #New position in decimal degrees
    newlat = original_location.lat + (dLat * 180/math.pi)
    newlon = original_location.lon + (dLon * 180/math.pi)
    return LocationGlobalRelative(newlat, newlon, original_location.alt)

def main():
    print("Connecting to Pixhawk...")
    vehicle = connect(CONNECTION_STRING, wait_ready=True, baud=BAUD_RATE)
    print("✓ Connected")

    # PRE-FLIGHT CHECKS
    print("Checking GPS...")
    if vehicle.gps_0.fix_type < 3:
        print("✗ NO GPS FIX! Cannot fly OUTDOOR mission.")
        print("  Go outside and wait for Blue/Green LED.")
        return

    print("\n" + "="*50)
    print("      READY FOR MISSION")
    print("      Waiting for GUIDED mode switch...")
    print("="*50)
    
    # 1. WAIT FOR PILOT
    while vehicle.mode.name != 'GUIDED':
        time.sleep(0.5)
        print(f"\rCurrent: {vehicle.mode.name}", end="")
    
    print("\n\n>>> STARTING MISSION <<<")
    
    try:
        # 2. ARM AND TAKEOFF
        print("Arming...")
        vehicle.armed = True
        while not vehicle.armed: time.sleep(1)
        
        print("Taking off to 5 meters...")
        vehicle.simple_takeoff(5)
        
        while True:
            alt = vehicle.location.global_relative_frame.alt
            print(f" Altitude: {alt:.1f}m")
            if alt >= 4.8: break
            time.sleep(1)

        # 3. SQUARE PATTERN
        print("\nFlying Square Pattern...")
        base_loc = vehicle.location.global_relative_frame
        
        # Waypoints: North 10m, East 10m, South 10m, West 10m
        moves = [(10, 0), (0, 10), (-10, 0), (0, -10)]
        
        for i, (north, east) in enumerate(moves):
            target = get_location_metres(vehicle.location.global_relative_frame, north, east)
            print(f" Going to Waypoint {i+1} (North:{north}, East:{east})...")
            vehicle.simple_goto(target)
            time.sleep(10) # Give time to fly there
            
            # Safety Check
            if vehicle.mode.name != 'GUIDED': raise Exception("Pilot Override")

        # 4. RTL
        print("\nMission Complete. Returning to Launch...")
        vehicle.mode = VehicleMode("RTL")
        
    except Exception as e:
        print(f"\n\n!!! ABORTED: {e} !!!")

    vehicle.close()

if __name__ == "__main__":
    main()

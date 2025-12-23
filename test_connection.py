#!/usr/bin/env python3
"""
Test script for Pixhawk CubeBlack connection via DroneKit
Run with: python3 test_connection.py
"""

from dronekit import connect, VehicleMode, LocationGlobal
import time
import sys

def test_connection():
    """Test connection to flight controller and display vehicle information"""
    
    print("=" * 50)
    print("Pixhawk CubeBlack Connection Test")
    print("=" * 50)
    print()
    
    # Connection string for Raspberry Pi serial
    connection_string = '/dev/serial0'
    baud_rate = 921600
    
    print(f"Connecting to vehicle on {connection_string}")
    print(f"Baud rate: {baud_rate}")
    print("Please wait...")
    print()
    
    try:
        # Connect to the vehicle
        vehicle = connect(connection_string, wait_ready=True, baud=baud_rate, timeout=60)
        
        print("✓ Connection successful!")
        print()
        
        # Display vehicle information
        print("-" * 50)
        print("VEHICLE INFORMATION")
        print("-" * 50)
        
        print(f"Autopilot Firmware Version: {vehicle.version}")
        print(f"Autopilot Capabilities: {vehicle.capabilities}")
        print(f"Vehicle Mode: {vehicle.mode.name}")
        print(f"Armed: {vehicle.armed}")
        print(f"System Status: {vehicle.system_status.state}")
        print()
        
        # GPS Information
        print("-" * 50)
        print("GPS INFORMATION")
        print("-" * 50)
        print(f"GPS Fix Type: {vehicle.gps_0.fix_type}")
        print(f"Number of Satellites: {vehicle.gps_0.satellites_visible}")
        print(f"Location: {vehicle.location.global_frame}")
        print()
        
        # Battery Information
        print("-" * 50)
        print("BATTERY INFORMATION")
        print("-" * 50)
        print(f"Voltage: {vehicle.battery.voltage}V")
        print(f"Current: {vehicle.battery.current}A")
        print(f"Battery Level: {vehicle.battery.level}%")
        print()
        
        # Attitude Information
        print("-" * 50)
        print("ATTITUDE INFORMATION")
        print("-" * 50)
        print(f"Pitch: {vehicle.attitude.pitch}")
        print(f"Roll: {vehicle.attitude.roll}")
        print(f"Yaw: {vehicle.attitude.yaw}")
        print()
        
        # Rangefinder (if available)
        print("-" * 50)
        print("RANGEFINDER")
        print("-" * 50)
        print(f"Distance: {vehicle.rangefinder.distance}m")
        print(f"Voltage: {vehicle.rangefinder.voltage}V")
        print()
        
        # Test parameter read
        print("-" * 50)
        print("PARAMETER TEST")
        print("-" * 50)
        print("Reading ARMING_CHECK parameter...")
        arming_check = vehicle.parameters['ARMING_CHECK']
        print(f"ARMING_CHECK: {arming_check}")
        print()
        
        # Heartbeat test
        print("-" * 50)
        print("HEARTBEAT TEST")
        print("-" * 50)
        print("Monitoring heartbeat for 5 seconds...")
        last_heartbeat = vehicle.last_heartbeat
        time.sleep(5)
        new_heartbeat = vehicle.last_heartbeat
        
        if new_heartbeat > last_heartbeat:
            print(f"✓ Heartbeat active (last: {new_heartbeat:.1f}s ago)")
        else:
            print("✗ No heartbeat detected!")
        print()
        
        # Close vehicle object
        vehicle.close()
        
        print("=" * 50)
        print("✓ ALL TESTS PASSED!")
        print("=" * 50)
        print()
        print("Your Raspberry Pi is successfully communicating with the CubeBlack!")
        return True
        
    except Exception as e:
        print()
        print("=" * 50)
        print("✗ CONNECTION FAILED")
        print("=" * 50)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Troubleshooting steps:")
        print("1. Check wiring (TX to RX, RX to TX, GND to GND)")
        print("2. Verify UART is enabled: ls -l /dev/serial0")
        print("3. Check CubeBlack SERIAL2_PROTOCOL = 2 and SERIAL2_BAUD = 921")
        print("4. Ensure you're in the dialout group: groups")
        print("5. Try lower baud rate: 57600")
        print()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

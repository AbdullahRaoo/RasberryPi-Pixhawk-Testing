#!/usr/bin/env python3
"""
RPi Hello World Test
--------------------
Sends "Hello World" from RPi → Pixhawk → SiK Radio → Dashboard.

Uses STATUSTEXT MAVLink message (Message ID: 253).
This is the same message type your dashboard already parses
in the mavlink/parser.py → shows up as status_text in DroneState.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from pymavlink import mavutil
import time

SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 57600

def main():
    print("Connecting to Pixhawk...")
    master = mavutil.mavlink_connection(
        SERIAL_PORT,
        baud=BAUD_RATE,
        source_system=1,
        source_component=191
    )
    
    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"✓ Connected\n")

    # Send companion heartbeat
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
        mavutil.mavlink.MAV_AUTOPILOT_INVALID,
        0, 0, 0
    )

    # Send "Hello World" as STATUSTEXT
    print("Sending: Hello World from RPi!")
    master.mav.statustext_send(
        mavutil.mavlink.MAV_SEVERITY_INFO,     # severity level
        b"Hello World from RPi!"               # text (max 50 chars)
    )
    time.sleep(0.5)

    # Send it 5 times to make sure it gets through
    for i in range(1, 6):
        msg = f"RPi says hello #{i}"
        print(f"Sending: {msg}")
        master.mav.statustext_send(
            mavutil.mavlink.MAV_SEVERITY_INFO,
            msg.encode('utf-8')[:50]
        )
        time.sleep(1)

    print("\n✓ Done! Check your dashboard for the messages.")

if __name__ == "__main__":
    main()

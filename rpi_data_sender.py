#!/usr/bin/env python3
"""
RPi Continuous Data Sender
--------------------------
DATA FLOW:
  RPi --serial (TELEM2)--> Pixhawk --SiK Radio (TELEM1)--> Dashboard

Sends continuous data at 4Hz:
  - NAMED_VALUE_FLOAT (sensor readings)
  - NAMED_VALUE_INT   (counters)
  - STATUSTEXT        (log messages, every 10 seconds)
  - HEARTBEAT         (companion alive signal, every 1 second)

Usage:
    python3 rpi_data_sender.py
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
    print(f"✓ Connected (System {master.target_system})")

    print("\n" + "="*50)
    print("  CONTINUOUS DATA STREAM")
    print("  RPi → Pixhawk → SiK Radio → Dashboard")
    print("  Sending at 4Hz. Press Ctrl+C to stop.")
    print("="*50 + "\n")

    msg_count = 0
    last_heartbeat = 0
    last_status = 0
    start_time = time.time()

    try:
        while True:
            now = time.time()
            elapsed = now - start_time

            # HEARTBEAT (1Hz) — Tells Pixhawk "RPi is alive"
            if now - last_heartbeat >= 1.0:
                master.mav.heartbeat_send(
                    mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
                    mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                    0, 0, 0
                )
                last_heartbeat = now

            # NAMED_VALUE_FLOAT (4Hz) — Continuous sensor data
            master.mav.named_value_float_send(
                int(now * 1000) & 0xFFFFFFFF,
                b'rpi_temp\x00\x00',
                20.0 + (elapsed % 10)  # Simulated: slowly rises 20→30°C
            )

            master.mav.named_value_float_send(
                int(now * 1000) & 0xFFFFFFFF,
                b'rpi_uptime',
                round(elapsed, 1)      # Uptime in seconds
            )

            # NAMED_VALUE_INT (4Hz) — Counter
            master.mav.named_value_int_send(
                int(now * 1000) & 0xFFFFFFFF,
                b'msg_count\x00',
                msg_count
            )

            # STATUSTEXT (Every 10 seconds) — Log message
            if now - last_status >= 10.0:
                text = f"RPi: {int(elapsed)}s uptime, {msg_count} msgs"
                master.mav.statustext_send(
                    mavutil.mavlink.MAV_SEVERITY_INFO,
                    text.encode('utf-8')[:50]
                )
                last_status = now
                print(f"  [{int(elapsed)}s] Sent STATUSTEXT: {text}")

            msg_count += 1
            if msg_count % 40 == 0:  # Print every 10 seconds (40 msgs at 4Hz)
                print(f"  [{int(elapsed)}s] Streaming... ({msg_count} msgs sent)")

            time.sleep(0.25)  # 4Hz

    except KeyboardInterrupt:
        print(f"\n✓ Stopped after {int(elapsed)}s. Total: {msg_count} messages.")

if __name__ == "__main__":
    main()

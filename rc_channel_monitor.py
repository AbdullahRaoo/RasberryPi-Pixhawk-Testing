#!/usr/bin/env python3
"""
RC Channel Monitor
------------------
Visualizes the RC inputs from your FlySky controller in real-time.
Use this to identify which Switch corresponds to which Channel.
"""

import collections
import collections.abc
if not hasattr(collections, 'MutableMapping'):
    collections.MutableMapping = collections.abc.MutableMapping

from dronekit import connect
import time
import sys
import os

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

    print("\n-------------------------------------------")
    print("      RC CHANNEL MONITOR")
    print("      Toggle your switches to see changes")
    print("-------------------------------------------")
    print("Channel 1 (Roll):     [Wait...]")
    print("Channel 2 (Pitch):    [Wait...]")
    print("Channel 3 (Throttle): [Wait...]")
    print("Channel 4 (Yaw):      [Wait...]")
    print("Channel 5 (Aux 1):    [Wait...]")
    print("Channel 6 (Aux 2):    [Wait...]")
    
    try:
        while True:
            # os.system('clear') # Optional: Clear screen for cleaner view
            # Read channels
            # DroneKit channels are 1-indexed dictionary
            rc = vehicle.channels
            
            # Print status on one line (or block)
            # \033[F moves cursor up to overwrite previous lines
            print(f"\rC1: {rc['1']} | C2: {rc['2']} | C3: {rc['3']} | C4: {rc['4']} | C5 (Mode?): \033[92m{rc['5']}\033[0m | C6: {rc['6']}", end="")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nDone.")
        vehicle.close()

if __name__ == "__main__":
    main()

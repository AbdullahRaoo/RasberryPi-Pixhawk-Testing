# Raspberry Pi & Pixhawk Setup

This repository contains tools and scripts for communicating with a Pixhawk CubeBlack via Raspberry Pi (DroneKit/MAVLink).

## 📂 Project Structure

### Active Scripts
| File | Description |
|------|-------------|
| `telemetry_monitor.py` | **SAFE**. Displays real-time sensor data (Attitude, Battery, GPS) without arming. |
| `mode_switcher.py` | **SAFE**. Tests bidirectional control by switching flight modes (Stabilize <-> Guided). |
| `pre_flight_check.py` | **PLANNED**. Automated safety checklist before flight. |

### 🛠️ Diagnostics (in `diagnostics/`)
Moved all debugging tools here to keep the root clean.
| File | Description |
|------|-------------|
| `hardware_test.sh` | Checks for raw serial data on the wire. |
| `diagnose_serial.sh` | Checks OS-level config (overlays, permissions). |
| `simple_loopback.py` | Tests RPi hardware loopback (requires jumper wire). |
| `test_connection.py` | Basic connection test script. |

## 🔌 Wiring & Configuration (Summary)
**Connection**: UART (TELEM2)
*   **Pixhawk** `SERIAL2_OPTIONS` = **0** (Flow Control Disabled)
*   **Pixhawk** `SERIAL2_BAUD` = **57** (57600)
*   **Wiring**: 3-Wire (TX->RX, RX->TX, GND->GND). **No 5V line.**

## 🚀 Usage
**Monitor Telemetry:**
```bash
python3 telemetry_monitor.py
```
**Test Control:**
```bash
python3 mode_switcher.py
```

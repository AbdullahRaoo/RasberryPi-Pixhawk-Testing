# Raspberry Pi + Pixhawk CubeBlack Drone Setup

Complete setup scripts and documentation for configuring a Raspberry Pi 4 Model B as a companion computer for Pixhawk CubeBlack flight controller.

## 🚀 Quick Start

```bash
# 1. Clone or download this repository to your Raspberry Pi
git clone https://github.com/yourusername/rpi-pixhawk-setup.git
cd rpi-pixhawk-setup

# 2. Run the installation script
bash install_drone_software.sh

# 3. Configure UART
sudo raspi-config
# Interface Options → Serial Port → NO for login, YES for hardware

# 4. Reboot
sudo reboot

# 5. Test connection
./test_mavproxy.sh
```

## 📁 Files

- **`README.md`** - This file
- **`SETUP_GUIDE.md`** - Complete setup instructions and troubleshooting
- **`WIRING_GUIDE.md`** - Hardware wiring diagrams and pinouts
- **`install_drone_software.sh`** - Automated installation script
- **`test_connection.py`** - DroneKit connection test script
- **`test_mavproxy.sh`** - MAVProxy connection test script

## 🔧 What Gets Installed

- Python 3 development tools
- MAVProxy (latest version)
- PyMAVLink (MAVLink Python library)
- DroneKit (Python API for drones)
- GStreamer (video streaming)
- System utilities (git, cmake, screen, htop)

## 📋 Requirements

### Hardware
- Raspberry Pi 4 Model B (2GB+ RAM recommended)
- Pixhawk CubeBlack flight controller
- MicroSD card (16GB+ recommended)
- Proper wiring between TELEM2 and RPi GPIO (see `WIRING_GUIDE.md`)
- Separate power supply for RPi (USB-C, 3A recommended)

### Software
- Raspberry Pi OS (Bookworm or later)
- Internet connection during installation
- SSH access to Raspberry Pi

## 🔌 Hardware Setup

Connect CubeBlack TELEM2 to Raspberry Pi GPIO:

| CubeBlack TELEM2 | Raspberry Pi 4 |
|------------------|----------------|
| TX (Pin 2)       | RX GPIO 15 (Pin 10) |
| RX (Pin 3)       | TX GPIO 14 (Pin 8) |
| GND (Pin 6)      | GND (Pin 6) |

**⚠️ Important:** Do NOT connect +5V. Power the RPi separately!

See `WIRING_GUIDE.md` for detailed diagrams and pinouts.

## ⚙️ Configuration Options

You can customize the installation by setting environment variables:

```bash
# Custom baud rate (default: 921600)
BAUDRATE=57600 bash install_drone_software.sh

# Skip video tools installation
INSTALL_VIDEO=no bash install_drone_software.sh

# Custom serial port (default: /dev/serial0)
SERIAL_PORT=/dev/ttyAMA0 bash install_drone_software.sh
```

## 📡 Flight Controller Setup

Connect to your CubeBlack with Mission Planner and set:

```
SERIAL2_PROTOCOL = 2    (MAVLink 2)
SERIAL2_BAUD = 921      (921600 baud)
```

## 🧪 Testing

### Test 1: Check Serial Port
```bash
ls -l /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0
```

### Test 2: MAVProxy Connection
```bash
./test_mavproxy.sh
```

### Test 3: DroneKit Script
```bash
python3 test_connection.py
```

## 🔄 Auto-Start Configuration

To enable MAVProxy on boot:

```bash
sudo systemctl enable mavproxy.service
sudo systemctl start mavproxy.service

# Check status
sudo systemctl status mavproxy.service

# View logs
journalctl -u mavproxy.service -f
```

## 🌐 Ground Station Connection

Once MAVProxy is running, connect from Mission Planner or QGroundControl:

- **Protocol:** UDP
- **IP Address:** (Your Raspberry Pi's IP)
- **Port:** 14550

Find your RPi IP: `hostname -I`

## 📚 Documentation

- **Full Setup Guide:** [`SETUP_GUIDE.md`](SETUP_GUIDE.md)
- **Wiring Instructions:** [`WIRING_GUIDE.md`](WIRING_GUIDE.md)
- **ArduPilot Docs:** https://ardupilot.org/dev/docs/raspberry-pi-via-mavlink.html
- **DroneKit-Python:** https://dronekit-python.readthedocs.io/
- **MAVProxy:** https://ardupilot.org/mavproxy/

## 🐛 Troubleshooting

### No response from vehicle
1. Check wiring (TX→RX, RX→TX, GND→GND)
2. Verify UART enabled: `ls -l /dev/serial0`
3. Check flight controller parameters (SERIAL2_PROTOCOL, SERIAL2_BAUD)
4. Try lower baud rate: `mavproxy.py --master=/dev/serial0 --baudrate=57600`

### Permission denied on /dev/serial0
```bash
sudo usermod -a -G dialout $USER
# Log out and back in, or reboot
```

### Installation logs
Check the installation log file for detailed error messages:
```bash
ls -lt ~/drone_setup_*.log | head -1
cat ~/drone_setup_*.log
```

## 🆘 Support

- **ArduPilot Discourse:** https://discuss.ardupilot.org/
- **DroneKit Forum:** https://discuss.dronekit.io/
- **Issues:** Open an issue on GitHub

## 📝 License

This project is provided as-is for educational purposes. 

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test your changes on actual hardware
4. Submit a pull request

## ⚠️ Safety Warning

Always follow drone safety guidelines:
- Test in a safe, open area
- Keep propellers off during development
- Follow local regulations
- Never fly over people or property
- Maintain line of sight

## 🔗 Related Projects

- [APSync](https://ardupilot.org/dev/docs/apsync-intro.html) - Complete companion computer image
- [Rpanion-server](https://www.docs.rpanion.com/) - Web-based configuration
- [MAVSDK](https://mavsdk.mavlink.io/) - Modern MAVLink SDK

## 📊 System Requirements

- **Raspberry Pi:** 4 Model B (1GB+), 3B+, or newer
- **OS:** Raspberry Pi OS Bookworm (64-bit recommended)
- **Storage:** 16GB+ microSD card
- **Network:** WiFi or Ethernet for initial setup
- **Power:** 5V 3A USB-C power supply

## 🎯 Tested Configurations

✅ Raspberry Pi 4 Model B (4GB) + CubeBlack + ArduCopter 4.5  
✅ Raspberry Pi 4 Model B (2GB) + CubeBlack + ArduPlane 4.5  
✅ Raspberry Pi OS Bookworm (64-bit)

---

**Version:** 1.0.0  
**Last Updated:** December 2025  
**Maintainer:** [Your Name]

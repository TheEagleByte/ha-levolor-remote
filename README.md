# Levolor BLE Remote Control

A Python library for controlling Levolor motorized blinds via Bluetooth Low Energy (BLE) communication with the Levolor 6-channel remote.

## Overview

This project reverse-engineers the BLE GATT protocol between the Levolor smartphone app and the Levolor 6-channel remote. The remote then transmits commands to the blinds via proprietary 2.4 GHz RF at 2453 MHz.

```
┌──────────┐     BLE/GATT      ┌──────────────┐    2.4GHz RF    ┌────────┐
│  Phone   │ ───────────────▶  │   Levolor    │ ──────────────▶ │ Blinds │
│  or PC   │                   │   Remote     │   (2453 MHz)    │        │
└──────────┘                   └──────────────┘                 └────────┘
```

## Requirements

- Python 3.8+
- Bluetooth adapter with BLE support
- Levolor 6-channel remote (paired with your blinds)

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Scan for Levolor devices
python levolor_ble.py scan

# Control blinds on channel 1
python levolor_ble.py open 1      # Open/raise blinds
python levolor_ble.py close 1     # Close/lower blinds
python levolor_ble.py stop 1      # Stop movement

# Control blinds on other channels (1-6)
python levolor_ble.py open 3      # Open channel 3
python levolor_ble.py close 5     # Close channel 5

# Specify remote address directly (faster, skips scan)
python levolor_ble.py -a E0:35:66:2E:F0:C4 open 1

# Verbose output for debugging
python levolor_ble.py -v open 1
```

### Python API

```python
import asyncio
from levolor_ble import LevolorRemote

async def main():
    # Using context manager (recommended)
    async with LevolorRemote() as remote:
        await remote.open(1)      # Open channel 1
        await asyncio.sleep(5)
        await remote.stop(1)      # Stop

asyncio.run(main())
```

Or with explicit connection management:

```python
async def main():
    remote = LevolorRemote()

    # Connect (scans automatically if no address provided)
    if await remote.connect():
        await remote.open(1)
        await asyncio.sleep(5)
        await remote.stop(1)
        await remote.disconnect()
```

## Protocol Documentation

### Device Information

| Property | Value |
|----------|-------|
| BLE Device Name | `Levolor` |
| Address Type | Random Device Address |

### GATT Structure

| UUID | Purpose |
|------|---------|
| `ab529101-5310-483a-b4d3-7f1eaa8134a0` | Initialization Characteristic (arms RF) |
| `ab529201-5310-483a-b4d3-7f1eaa8134a0` | Command Characteristic |

### Command Format

Commands are 3-byte payloads written to the command characteristic:

```
Byte 0: 0xF1 (prefix, always the same)
Byte 1: Action code
Byte 2: Channel number (0x01-0x06)
```

### Action Codes

| Action | Code | Verified |
|--------|------|----------|
| Open (Up) | `0x01` | Yes |
| Close (Down) | `0x02` | Yes |
| Stop | `0x06` | Yes |
| Tilt Open | `0x03` | Not tested |
| Tilt Close | `0x04` | Not tested |
| Favorite | `0x05` | Not tested |

### Example Commands

```python
OPEN_CH1  = bytes([0xF1, 0x01, 0x01])  # f10101
CLOSE_CH1 = bytes([0xF1, 0x02, 0x01])  # f10201
STOP_CH1  = bytes([0xF1, 0x06, 0x01])  # f10601
OPEN_CH3  = bytes([0xF1, 0x01, 0x03])  # f10103
```

## Reverse Engineering Process

### How This Protocol Was Discovered

1. **Captured BLE traffic** using Android's HCI snoop log feature (Developer Options > Enable Bluetooth HCI snoop log)

2. **Extracted the log** via ADB:
   ```bash
   adb bugreport capture.zip
   # Extract btsnoop_hci.log from the zip
   ```

3. **Analyzed with tshark**:
   ```bash
   # List ATT operations
   tshark -r btsnooz_hci.log -Y "btatt.opcode == 0x12 || btatt.opcode == 0x52"

   # Extract write values
   tshark -r btsnooz_hci.log -Y "btatt" -T fields \
     -e frame.time -e btatt.opcode -e btatt.handle -e btatt.value
   ```

4. **Correlated timestamps** with physical button presses (down, stop, up)

5. **Identified the pattern**:
   - All commands start with `0xF1`
   - Second byte changes based on action
   - Third byte is the channel number

### Key Findings

- **Initialization IS required**: After connecting, you must write `0x88 0xFA` to characteristic `ab529101` to arm the RF transmitter. Without this, BLE commands succeed but the remote won't broadcast RF to the blinds.

- **No pairing required**: Standard BLE connection works. Explicit pairing with `bluetoothctl pair` can actually cause issues.

- **UUID-based writes work best**: Using characteristic UUIDs rather than handles ensures compatibility across different connection sessions (handles can change).

- **Write with response preferred**: The characteristic supports both write-with-response and write-without-response. We try with-response first and fall back if needed.

### Comparison to Directolor RF Protocol

The [Directolor project](https://github.com/vbrvk/Directolor) documents the RF protocol from the remote to the blinds. The BLE protocol uses different action codes:

| Action | RF Code | BLE Code |
|--------|---------|----------|
| Open | `0x55` | `0x01` |
| Close | `0x44` | `0x02` |
| Stop | `0x53` | `0x06` |

## Troubleshooting

### "No Levolor devices found"

- Ensure the remote has batteries and is powered on
- Check that Bluetooth is enabled on your computer
- Move closer to the remote
- Make sure no other device (phone) is currently connected to the remote

### "Connection failed" or "Unlikely Error"

- Disconnect from the remote on your phone (turn off Bluetooth on phone)
- Only one device can be connected to the remote at a time
- Try removing cached device: `bluetoothctl remove E0:35:66:2E:F0:C4`

### Commands sent but blinds don't move

- Verify the channel number matches how the blind is programmed on the remote
- Press the physical button on the remote to confirm RF communication is working
- The remote may need to be re-paired with the blinds

## Files in This Project

| File | Purpose |
|------|---------|
| `levolor_ble.py` | Main Python BLE client |
| `requirements.txt` | Python dependencies |
| `README.md` | This documentation |
| `PROTOCOL.md` | Raw protocol notes |
| `btsnooz_hci.log` | Captured BLE traffic (for reference) |
| `venv/` | Python virtual environment |

## Future Work

- Home Assistant integration (custom component)
- Test tilt and favorite commands
- Support for "all channels" command
- Position feedback (if available via notifications)

## License

MIT License - Use at your own risk. This is a reverse-engineered protocol and may break with firmware updates.

# Levolor BLE

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for controlling Levolor motorized blinds via Bluetooth Low Energy (BLE).

## How It Works

This integration communicates with the Levolor 6-channel remote via BLE. The remote then transmits commands to your blinds using RF.

```
┌──────────────┐     BLE/GATT      ┌──────────────┐    2.4GHz RF    ┌────────┐
│    Home      │ ───────────────▶  │   Levolor    │ ──────────────▶ │ Blinds │
│  Assistant   │                   │   Remote     │   (2453 MHz)    │        │
└──────────────┘                   └──────────────┘                 └────────┘
```

## Features

- Automatic discovery of Levolor remotes
- Control up to 6 channels per remote
- Open, close, and stop commands
- State persistence across restarts
- Supports Bluetooth proxies for extended range

## Requirements

- Home Assistant 2023.8.0+
- Bluetooth adapter with BLE support
- Levolor 6-channel remote (paired with your blinds)

## Quick Start

### Installation

**HACS (Recommended):**
1. Add this repository as a custom repository in HACS
2. Install "Levolor BLE"
3. Restart Home Assistant

**Manual:**
1. Copy `custom_components/levolor_ble` to your `config/custom_components/` directory
2. Restart Home Assistant

See the [Installation Guide](docs/installation.md) for detailed instructions.

### Setup

1. Ensure your Levolor remote has batteries and is within Bluetooth range
2. Disconnect any phone apps from the remote (only one BLE connection allowed)
3. Home Assistant will auto-discover the remote, or add it manually via **Settings** → **Devices & Services**
4. Configure a name and channel for each blind

See the [Configuration Guide](docs/configuration.md) for detailed setup instructions.

## Documentation

| Document | Description |
|----------|-------------|
| [Installation](docs/installation.md) | Installation methods and requirements |
| [Configuration](docs/configuration.md) | Setting up blinds and automations |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |
| [Protocol](docs/protocol.md) | BLE protocol technical details |

## Standalone Usage

A standalone Python script is also included for testing and command-line control:

```bash
# Install dependencies
pip install bleak

# Scan for devices
python levolor_ble.py scan

# Control blinds
python levolor_ble.py open 1    # Open channel 1
python levolor_ble.py close 1   # Close channel 1
python levolor_ble.py stop 1    # Stop movement
```

## Supported Commands

| Command | Description |
|---------|-------------|
| Open | Raise the blind |
| Close | Lower the blind |
| Stop | Stop movement |
| Tilt Open* | Open slats |
| Tilt Close* | Close slats |
| Favorite* | Go to preset position |

*Not all blinds support tilt/favorite commands

## Known Limitations

- **No position feedback**: The protocol doesn't report blind position, so state is estimated
- **Single connection**: Only one device can connect to the remote at a time
- **RF range**: The remote must be within RF range of the blinds (usually same room)

## Contributing

Contributions are welcome! Please open an issue or pull request.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- Protocol reverse-engineered via BLE packet capture
- Inspired by the [Directolor](https://github.com/vbrvk/Directolor) RF protocol documentation

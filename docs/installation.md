# Installation

This guide covers installing the Levolor BLE integration for Home Assistant.

## Prerequisites

- Home Assistant 2023.8.0 or newer
- Bluetooth adapter with BLE support on your Home Assistant host
- Levolor 6-channel remote (already paired with your blinds)

## Installation Methods

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu in the top right
3. Select **Custom repositories**
4. Add this repository URL and select **Integration** as the category
5. Click **Add**
6. Search for "Levolor BLE" in HACS and install it
7. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the `custom_components/levolor_ble` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

Your directory structure should look like:
```
config/
├── configuration.yaml
└── custom_components/
    └── levolor_ble/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── cover.py
        ├── manifest.json
        ├── strings.json
        └── translations/
            └── en.json
```

## Verifying Installation

After restarting Home Assistant:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Levolor"
4. If the integration appears, installation was successful

## Next Steps

- [Configuration Guide](configuration.md) - Set up your blinds
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

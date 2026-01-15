# Configuration

This guide explains how to configure the Levolor BLE integration after installation.

## Adding Your Remote

### Automatic Discovery

Home Assistant will automatically discover Levolor remotes that are:
- Powered on (has batteries)
- Within Bluetooth range
- Not connected to another device (phone app)

When discovered, you'll see a notification in Home Assistant to configure the device.

### Manual Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Levolor BLE"
4. Select your Levolor remote from the list
5. Configure the blind (see below)

## Configuring a Blind

When adding a blind, you'll be prompted for:

| Field | Description |
|-------|-------------|
| **Blind Name** | A friendly name for the blind (e.g., "Living Room Blinds") |
| **Channel** | The channel (1-6) this blind is programmed to on the remote |

### Understanding Channels

The Levolor 6-channel remote can control up to 6 blinds or groups of blinds. Each blind must be programmed to a specific channel using the physical remote. The channel you select in Home Assistant must match the channel the blind responds to on the remote.

To verify which channel a blind uses:
1. Press the channel button on your physical remote
2. Press up/down and observe which blind moves

## Adding Multiple Blinds

Each blind requires a separate config entry. To add another blind on the same remote:

1. Go to **Settings** → **Devices & Services**
2. Find "Levolor BLE" and click **Configure** or **Add Entry**
3. The same remote will be detected again
4. Configure a different name and channel

All blinds on the same remote will appear under one device in Home Assistant.

## Entity Features

Each blind is created as a `cover` entity with the following capabilities:

| Feature | Description |
|---------|-------------|
| **Open** | Raise the blind fully |
| **Close** | Lower the blind fully |
| **Stop** | Stop blind movement |
| **Set Position** | Approximate positioning (opens if >= 50%, closes if < 50%) |

### State Tracking

Since the Levolor protocol doesn't provide position feedback, the integration uses assumed state:
- Position is estimated based on last command sent
- State is persisted across Home Assistant restarts
- Actual blind position may differ if controlled via physical remote

## Automations

Example automation to close blinds at sunset:

```yaml
automation:
  - alias: "Close blinds at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: cover.close_cover
        target:
          entity_id: cover.living_room_blinds
```

Example automation to open blinds in the morning:

```yaml
automation:
  - alias: "Open blinds in morning"
    trigger:
      - platform: time
        at: "07:00:00"
    condition:
      - condition: workday
    action:
      - service: cover.open_cover
        target:
          entity_id: cover.living_room_blinds
```

## Services

The integration uses standard cover services:

| Service | Description |
|---------|-------------|
| `cover.open_cover` | Open/raise the blind |
| `cover.close_cover` | Close/lower the blind |
| `cover.stop_cover` | Stop blind movement |
| `cover.set_cover_position` | Set position (0-100, approximate) |

## Next Steps

- [Troubleshooting](troubleshooting.md) - If you encounter issues
- [Protocol Documentation](protocol.md) - Technical protocol details

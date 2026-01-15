# Levolor BLE Protocol Specification

Technical protocol details discovered through reverse engineering.

## Device Discovery

| Property | Value |
|----------|-------|
| Device Name | `Levolor` |
| Address Type | Random Device Address |
| Example MAC | `E0:35:66:2E:F0:C4` |

Note: The MAC address uses BLE Random Address type and may change.

## GATT Services

The remote exposes multiple services following the UUID pattern `ab5291XX-5310-483a-b4d3-7f1eaa8134a0`:

| Service UUID | Purpose |
|--------------|---------|
| `ab529100-...` | Unknown |
| `ab529200-...` | **Command Service** |
| `ab529300-...` | Unknown |
| `ab529400-...` | Unknown |

## Initialization Service (ab529100-...)

### Initialization Characteristic

| Property | Value |
|----------|-------|
| UUID | `ab529101-5310-483a-b4d3-7f1eaa8134a0` |
| Properties | Write |
| Payload | `0x88 0xFA` |
| Purpose | Arms the RF transmitter |

This write must be sent after connecting and before sending commands. Without it, the remote accepts BLE commands but does not transmit RF to the blinds.

## Command Service (ab529200-...)

### Command Characteristic

| Property | Value |
|----------|-------|
| UUID | `ab529201-5310-483a-b4d3-7f1eaa8134a0` |
| Properties | Read, Write |

## Command Packet Format

```
┌─────────┬─────────┬─────────┐
│ Prefix  │ Action  │ Channel │
│  0xF1   │  0xXX   │  0xXX   │
└─────────┴─────────┴─────────┘
   Byte 0    Byte 1    Byte 2
```

### Prefix Byte (0)

Always `0xF1`.

### Action Byte (1)

| Action | Code | Status |
|--------|------|--------|
| Open (Up) | `0x01` | Verified |
| Close (Down) | `0x02` | Verified |
| Tilt Open | `0x03` | Untested |
| Tilt Close | `0x04` | Untested |
| Favorite | `0x05` | Untested |
| Stop | `0x06` | Verified |

### Channel Byte (2)

| Channel | Code |
|---------|------|
| Channel 1 | `0x01` |
| Channel 2 | `0x02` |
| Channel 3 | `0x03` |
| Channel 4 | `0x04` |
| Channel 5 | `0x05` |
| Channel 6 | `0x06` |
| All Channels | `0x00` (unverified) |

## Example Commands

| Command | Bytes | Hex |
|---------|-------|-----|
| Open Channel 1 | `[0xF1, 0x01, 0x01]` | `f10101` |
| Close Channel 1 | `[0xF1, 0x02, 0x01]` | `f10201` |
| Stop Channel 1 | `[0xF1, 0x06, 0x01]` | `f10601` |
| Open Channel 3 | `[0xF1, 0x01, 0x03]` | `f10103` |
| Close Channel 6 | `[0xF1, 0x02, 0x06]` | `f10206` |

## Connection Procedure

1. Scan for BLE device with name containing "Levolor"
2. Connect to device (no pairing required)
3. **Write initialization** `0x88 0xFA` to characteristic `ab529101-...` (arms RF transmitter)
4. Write 3-byte command to characteristic `ab529201-...`
5. Disconnect when done

The initialization step is required - without it, BLE communication succeeds but the remote won't transmit RF to the blinds.

## Protocol Notes

### Write Method

The characteristic accepts both:
- Write Request (ATT opcode `0x12`) - with acknowledgment
- Write Command (ATT opcode `0x52`) - without acknowledgment

Write Request is preferred for reliability.

### Connection Exclusivity

Only one BLE device can connect to the remote at a time. If a phone is connected, the computer cannot connect (and vice versa).

### Random Address

The remote uses a BLE Random Device Address. The address may change after:
- Battery replacement
- Factory reset
- Extended periods of non-use

Scanning by device name is more reliable than hardcoding the MAC address.

## RF Protocol (Remote to Blinds)

The remote communicates with blinds via proprietary 2.4 GHz RF at 2453 MHz. This is a separate protocol documented by the [Directolor project](https://github.com/vbrvk/Directolor).

The BLE action codes differ from RF action codes:

| Action | BLE Code | RF Code |
|--------|----------|---------|
| Open | `0x01` | `0x55` |
| Close | `0x02` | `0x44` |
| Stop | `0x06` | `0x53` |
| Tilt Open | `0x03` | `0x52` |
| Tilt Close | `0x04` | `0x4C` |
| Favorite | `0x05` | `0x48` |

## Capture Methodology

Protocol discovered by:

1. Enabling HCI snoop log on Android (Developer Options)
2. Performing actions in official Levolor app
3. Extracting log via `adb bugreport`
4. Analyzing ATT Write operations with tshark
5. Correlating timestamps with physical actions
6. Testing hypotheses with Python/Bleak client

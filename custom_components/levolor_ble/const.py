"""Constants for the Levolor BLE Blinds integration."""

from enum import IntEnum

DOMAIN = "levolor_ble"

# Device identification
LEVOLOR_DEVICE_NAME = "Levolor"

# GATT Characteristic UUIDs
COMMAND_CHAR_UUID = "ab529201-5310-483a-b4d3-7f1eaa8134a0"
INIT_CHAR_UUID = "ab529101-5310-483a-b4d3-7f1eaa8134a0"

# Protocol constants
INIT_PAYLOAD = bytes([0x88, 0xFA])
CMD_PREFIX = 0xF1

# Connection settings
DEFAULT_RETRY_COUNT = 3
COMMAND_DELAY = 0.3  # seconds to wait after command before disconnect


class Action(IntEnum):
    """Blind action codes for BLE protocol."""

    OPEN = 0x01
    CLOSE = 0x02
    TILT_OPEN = 0x03
    TILT_CLOSE = 0x04
    FAVORITE = 0x05
    STOP = 0x06


# Config entry keys
CONF_ADDRESS = "address"
CONF_CHANNEL = "channel"
CONF_BLIND_NAME = "blind_name"

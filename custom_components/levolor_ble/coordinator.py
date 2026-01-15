"""BLE connection coordinator for Levolor blinds."""

from __future__ import annotations

import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CMD_PREFIX,
    COMMAND_CHAR_UUID,
    COMMAND_DELAY,
    DEFAULT_RETRY_COUNT,
    INIT_CHAR_UUID,
    INIT_PAYLOAD,
    LEVOLOR_DEVICE_NAME,
    Action,
)

_LOGGER = logging.getLogger(__name__)


class LevolorBLECoordinator:
    """Coordinate BLE connections to Levolor remote."""

    def __init__(self, hass: HomeAssistant, address: str) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.address = address
        self._lock = asyncio.Lock()

    async def async_send_command(
        self, action: Action, channel: int, retry_count: int = DEFAULT_RETRY_COUNT
    ) -> bool:
        """Send a command to the Levolor remote with retry logic."""
        async with self._lock:
            for attempt in range(retry_count):
                try:
                    success = await self._send_command_once(action, channel)
                    if success:
                        return True
                except (BleakError, TimeoutError) as err:
                    _LOGGER.warning(
                        "Attempt %d/%d failed for %s channel %d: %s",
                        attempt + 1,
                        retry_count,
                        action.name,
                        channel,
                        err,
                    )
                    if attempt < retry_count - 1:
                        await asyncio.sleep(1.0)

            _LOGGER.error(
                "Failed to send %s to channel %d after %d attempts",
                action.name,
                channel,
                retry_count,
            )
            return False

    async def _send_command_once(self, action: Action, channel: int) -> bool:
        """Send a single command to the remote."""
        # Get BLE device from Home Assistant's Bluetooth integration
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

        if not ble_device:
            # Try to find device by name if address not found
            ble_device = await self._find_device_by_name()

        if not ble_device:
            raise HomeAssistantError(
                f"Levolor remote not found at {self.address}. "
                "Ensure it's powered on and nearby."
            )

        async with BleakClient(ble_device) as client:
            # Initialize RF transmitter
            _LOGGER.debug("Sending initialization payload")
            await client.write_gatt_char(INIT_CHAR_UUID, INIT_PAYLOAD)

            # Build and send command
            command = bytes([CMD_PREFIX, action, channel])
            _LOGGER.debug(
                "Sending %s to channel %d: %s", action.name, channel, command.hex()
            )

            try:
                await client.write_gatt_char(COMMAND_CHAR_UUID, command, response=True)
            except BleakError:
                # Fall back to write without response
                await client.write_gatt_char(COMMAND_CHAR_UUID, command, response=False)

            # Allow remote to process before disconnect
            await asyncio.sleep(COMMAND_DELAY)

            _LOGGER.info("Successfully sent %s to channel %d", action.name, channel)
            return True

    async def _find_device_by_name(self):
        """Find Levolor device by name when address lookup fails."""
        _LOGGER.debug("Searching for Levolor device by name")
        discoveries = bluetooth.async_discovered_service_info(
            self.hass, connectable=True
        )
        for discovery in discoveries:
            if discovery.name and LEVOLOR_DEVICE_NAME in discovery.name:
                _LOGGER.info(
                    "Found Levolor device at new address: %s", discovery.address
                )
                self.address = discovery.address
                return discovery.device
        return None

    async def async_test_connection(self) -> bool:
        """Test if we can connect to the device."""
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )

        if not ble_device:
            ble_device = await self._find_device_by_name()

        if not ble_device:
            return False

        try:
            async with BleakClient(ble_device) as client:
                # Just try to send init to verify connection works
                await client.write_gatt_char(INIT_CHAR_UUID, INIT_PAYLOAD)
                return True
        except BleakError as err:
            _LOGGER.debug("Connection test failed: %s", err)
            return False

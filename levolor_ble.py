#!/usr/bin/env python3
"""
Levolor BLE Remote Control Client

This module provides a Python interface to control Levolor motorized blinds
via BLE communication with the Levolor 6-channel remote.

Usage:
    python levolor_ble.py scan           # Scan for Levolor devices
    python levolor_ble.py open 1         # Open channel 1
    python levolor_ble.py close 1        # Close channel 1
    python levolor_ble.py stop 1         # Stop channel 1
"""

import asyncio
import argparse
import logging
from enum import IntEnum
from typing import Optional

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Levolor BLE Protocol Constants
LEVOLOR_DEVICE_NAME = "Levolor"

# GATT Characteristic UUIDs (discovered from protocol analysis)
COMMAND_CHAR_UUID = "ab529201-5310-483a-b4d3-7f1eaa8134a0"  # For sending commands
INIT_CHAR_UUID = "ab529101-5310-483a-b4d3-7f1eaa8134a0"     # For arming RF transmitter

# Initialization payload - arms the RF transmitter so commands reach the blinds
INIT_PAYLOAD = bytes([0x88, 0xFA])

# Command prefix
CMD_PREFIX = 0xF1


class Action(IntEnum):
    """Blind action codes for BLE protocol."""
    OPEN = 0x01
    CLOSE = 0x02
    STOP = 0x06
    # These are guesses based on RF protocol patterns
    TILT_OPEN = 0x03
    TILT_CLOSE = 0x04
    FAVORITE = 0x05


class LevolorRemote:
    """
    BLE client for Levolor motorized blind remote control.

    This class provides methods to connect to a Levolor remote and
    send commands to control blinds on different channels.

    Can be used as an async context manager:
        async with LevolorRemote() as remote:
            await remote.open(1)
    """

    def __init__(self, address: Optional[str] = None):
        """
        Initialize the Levolor remote client.

        Args:
            address: BLE MAC address of the remote. If None, will scan for device.
        """
        self.address = address
        self.client: Optional[BleakClient] = None

    async def __aenter__(self) -> "LevolorRemote":
        """Async context manager entry - connects to the remote."""
        if not await self.connect():
            raise BleakError("Failed to connect to Levolor remote")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - disconnects from the remote."""
        await self.disconnect()

    @staticmethod
    async def scan(timeout: float = 10.0) -> list:
        """
        Scan for Levolor devices.

        Args:
            timeout: Scan duration in seconds.

        Returns:
            List of discovered Levolor devices.
        """
        logger.info(f"Scanning for Levolor devices ({timeout}s)...")
        devices = []

        async with BleakScanner() as scanner:
            await asyncio.sleep(timeout)
            discovered = scanner.discovered_devices

        for device in discovered:
            if device.name and LEVOLOR_DEVICE_NAME in device.name:
                logger.info(f"Found: {device.name} ({device.address})")
                devices.append(device)

        if not devices:
            logger.warning("No Levolor devices found")

        return devices

    @staticmethod
    async def find_device(timeout: float = 10.0):
        """
        Find the first Levolor device.

        Args:
            timeout: Scan duration in seconds.

        Returns:
            The first discovered Levolor device, or None if not found.
        """
        logger.info(f"Searching for Levolor device ({timeout}s)...")

        device = await BleakScanner.find_device_by_filter(
            lambda d, _: d.name and LEVOLOR_DEVICE_NAME in d.name,
            timeout=timeout
        )

        if device:
            logger.info(f"Found: {device.name} ({device.address})")
        else:
            logger.warning("No Levolor device found")

        return device

    async def connect(self, timeout: float = 10.0) -> bool:
        """
        Connect to the Levolor remote.

        Args:
            timeout: Connection timeout in seconds (used for scanning if no address).

        Returns:
            True if connection successful, False otherwise.
        """
        if self.address is None:
            # Find first available device (more efficient than full scan)
            device = await self.find_device(timeout=timeout)
            if not device:
                logger.error("No Levolor device found to connect to")
                return False
            self.address = device.address

        logger.info(f"Connecting to {self.address}...")

        try:
            self.client = BleakClient(self.address)
            await self.client.connect()

            if not self.client.is_connected:
                logger.error("Failed to connect")
                return False

            # Services are auto-discovered after connect
            logger.debug(f"Services: {[s.uuid for s in self.client.services]}")

            # Send initialization (required to enable RF transmission)
            try:
                await self.client.write_gatt_char(INIT_CHAR_UUID, INIT_PAYLOAD)
                logger.debug("Initialization sent")
            except Exception as e:
                logger.debug(f"Init write note: {e}")

            logger.info("Connected successfully")
            return True
        except BleakError as e:
            logger.error(f"Connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the remote."""
        if self.client and self.client.is_connected:
            await self.client.disconnect()
            logger.info("Disconnected")

    async def send_command(self, action: Action, channel: int) -> bool:
        """
        Send a command to the remote.

        Args:
            action: The action to perform (OPEN, CLOSE, STOP, etc.)
            channel: Channel number (1-6)

        Returns:
            True if command sent successfully.
        """
        if not self.client or not self.client.is_connected:
            logger.error("Not connected")
            return False

        if channel < 1 or channel > 6:
            logger.error(f"Invalid channel: {channel}. Must be 1-6.")
            return False

        # Build command: [PREFIX] [ACTION] [CHANNEL]
        command = bytes([CMD_PREFIX, action, channel])

        try:
            logger.info(f"Sending {action.name} to channel {channel}: {command.hex()}")
            # Try write with response first, fall back to without response
            try:
                await self.client.write_gatt_char(COMMAND_CHAR_UUID, command, response=True)
            except Exception:
                await self.client.write_gatt_char(COMMAND_CHAR_UUID, command, response=False)
            # Small delay to let the remote process the command before disconnect
            await asyncio.sleep(0.5)
            logger.info("Command sent successfully")
            return True
        except BleakError as e:
            logger.error(f"Command failed: {e}")
            return False

    # Convenience methods
    async def open(self, channel: int) -> bool:
        """Open blinds on specified channel."""
        return await self.send_command(Action.OPEN, channel)

    async def close(self, channel: int) -> bool:
        """Close blinds on specified channel."""
        return await self.send_command(Action.CLOSE, channel)

    async def stop(self, channel: int) -> bool:
        """Stop blinds on specified channel."""
        return await self.send_command(Action.STOP, channel)

    async def tilt_open(self, channel: int) -> bool:
        """Tilt blinds open on specified channel."""
        return await self.send_command(Action.TILT_OPEN, channel)

    async def tilt_close(self, channel: int) -> bool:
        """Tilt blinds closed on specified channel."""
        return await self.send_command(Action.TILT_CLOSE, channel)

    async def favorite(self, channel: int) -> bool:
        """Move blinds to favorite position on specified channel."""
        return await self.send_command(Action.FAVORITE, channel)


async def main():
    """Command-line interface for Levolor remote control."""
    parser = argparse.ArgumentParser(description="Levolor BLE Remote Control")
    parser.add_argument("command", choices=["scan", "open", "close", "stop", "tilt_open", "tilt_close", "favorite"],
                        help="Command to execute")
    parser.add_argument("channel", type=int, nargs="?", default=1,
                        help="Channel number (1-6)")
    parser.add_argument("--address", "-a", type=str,
                        help="BLE address of Levolor remote")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    remote = LevolorRemote(address=args.address)

    if args.command == "scan":
        await remote.scan()
        return

    # Connect and execute command
    if not await remote.connect():
        return

    try:
        if args.command == "open":
            await remote.open(args.channel)
        elif args.command == "close":
            await remote.close(args.channel)
        elif args.command == "stop":
            await remote.stop(args.channel)
        elif args.command == "tilt_open":
            await remote.tilt_open(args.channel)
        elif args.command == "tilt_close":
            await remote.tilt_close(args.channel)
        elif args.command == "favorite":
            await remote.favorite(args.channel)
    finally:
        await remote.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

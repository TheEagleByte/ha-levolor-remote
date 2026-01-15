"""Config flow for Levolor BLE Blinds integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import CONF_BLIND_NAME, CONF_CHANNEL, DOMAIN, LEVOLOR_DEVICE_NAME

_LOGGER = logging.getLogger(__name__)


class LevolorBLEConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Levolor BLE Blinds."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the Bluetooth discovery step."""
        _LOGGER.debug("Discovered Levolor device: %s", discovery_info.address)
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name or "Levolor"}

        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Bluetooth discovery and configure channel."""
        assert self._discovery_info is not None

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_BLIND_NAME],
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    CONF_CHANNEL: user_input[CONF_CHANNEL],
                    CONF_BLIND_NAME: user_input[CONF_BLIND_NAME],
                },
            )

        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BLIND_NAME, default="Levolor Blind"): str,
                    vol.Required(CONF_CHANNEL, default=1): vol.In(
                        {1: "Channel 1", 2: "Channel 2", 3: "Channel 3",
                         4: "Channel 4", 5: "Channel 5", 6: "Channel 6"}
                    ),
                }
            ),
            description_placeholders={
                "name": self._discovery_info.name or "Levolor",
                "address": self._discovery_info.address,
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user-initiated flow."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address)
            self._abort_if_unique_id_configured()

            # Store selection and proceed to channel config
            self._discovery_info = self._discovered_devices.get(address)
            return await self.async_step_configure()

        # Scan for available Levolor devices
        self._discovered_devices = {}
        for discovery in async_discovered_service_info(self.hass, connectable=True):
            if discovery.name and LEVOLOR_DEVICE_NAME in discovery.name:
                self._discovered_devices[discovery.address] = discovery

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        # Build selection list
        device_options = {
            addr: f"{info.name} ({addr})"
            for addr, info in self._discovered_devices.items()
        }

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(device_options),
                }
            ),
            errors=errors,
        )

    async def async_step_configure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Configure channel and name for the blind."""
        if user_input is not None:
            assert self._discovery_info is not None
            return self.async_create_entry(
                title=user_input[CONF_BLIND_NAME],
                data={
                    CONF_ADDRESS: self._discovery_info.address,
                    CONF_CHANNEL: user_input[CONF_CHANNEL],
                    CONF_BLIND_NAME: user_input[CONF_BLIND_NAME],
                },
            )

        return self.async_show_form(
            step_id="configure",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BLIND_NAME, default="Levolor Blind"): str,
                    vol.Required(CONF_CHANNEL, default=1): vol.In(
                        {1: "Channel 1", 2: "Channel 2", 3: "Channel 3",
                         4: "Channel 4", 5: "Channel 5", 6: "Channel 6"}
                    ),
                }
            ),
        )

"""Cover platform for Levolor BLE Blinds."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_ADDRESS, CONF_BLIND_NAME, CONF_CHANNEL, DOMAIN, Action
from .coordinator import LevolorBLECoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Levolor BLE cover from a config entry."""
    coordinator: LevolorBLECoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            LevolorBlindCover(
                coordinator=coordinator,
                address=entry.data[CONF_ADDRESS],
                channel=entry.data[CONF_CHANNEL],
                name=entry.data[CONF_BLIND_NAME],
                entry_id=entry.entry_id,
            )
        ]
    )


class LevolorBlindCover(CoverEntity, RestoreEntity):
    """Representation of a Levolor blind."""

    _attr_device_class = CoverDeviceClass.BLIND
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )
    _attr_assumed_state = True
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LevolorBLECoordinator,
        address: str,
        channel: int,
        name: str,
        entry_id: str,
    ) -> None:
        """Initialize the cover."""
        self._coordinator = coordinator
        self._address = address
        self._channel = channel
        self._entry_id = entry_id

        # Entity attributes
        self._attr_name = None  # Use device name as entity name
        self._attr_unique_id = f"{address}_{channel}"
        self._attr_current_cover_position: int | None = None
        self._attr_is_closed: bool | None = None
        self._attr_is_opening = False
        self._attr_is_closing = False
        self._attr_available = True

        # Device info - groups all channels under one device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            name=name,
            manufacturer="Levolor",
            model="6-Channel BLE Remote",
        )

    async def async_added_to_hass(self) -> None:
        """Restore state when entity is added."""
        await super().async_added_to_hass()

        # Restore previous state
        if (last_state := await self.async_get_last_state()) is not None:
            if (position := last_state.attributes.get(ATTR_POSITION)) is not None:
                self._attr_current_cover_position = position
                self._attr_is_closed = position == 0

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the blind."""
        self._attr_is_opening = True
        self._attr_is_closing = False
        self.async_write_ha_state()

        success = await self._coordinator.async_send_command(
            Action.OPEN, self._channel
        )

        self._attr_is_opening = False
        if success:
            self._attr_current_cover_position = 100
            self._attr_is_closed = False
            self._attr_available = True
        else:
            self._attr_available = False

        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the blind."""
        self._attr_is_closing = True
        self._attr_is_opening = False
        self.async_write_ha_state()

        success = await self._coordinator.async_send_command(
            Action.CLOSE, self._channel
        )

        self._attr_is_closing = False
        if success:
            self._attr_current_cover_position = 0
            self._attr_is_closed = True
            self._attr_available = True
        else:
            self._attr_available = False

        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the blind."""
        self._attr_is_opening = False
        self._attr_is_closing = False

        success = await self._coordinator.async_send_command(
            Action.STOP, self._channel
        )

        if success:
            self._attr_available = True
        else:
            self._attr_available = False

        self.async_write_ha_state()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Set cover position (approximate - open if >= 50%, else close)."""
        position = kwargs.get(ATTR_POSITION, 50)

        if position >= 50:
            await self.async_open_cover()
        else:
            await self.async_close_cover()

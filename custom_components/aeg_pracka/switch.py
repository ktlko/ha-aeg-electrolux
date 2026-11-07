"""Switches generated from writable on/off capabilities."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry, generic
from .entity import GeneratedEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        GeneratedSwitch(coordinator, appliance_id, s)
        for appliance_id, w in coordinator.washers.items()
        for s in generic.specs(w)
        if s.platform == "switch"
    )


class GeneratedSwitch(GeneratedEntity, SwitchEntity):
    """Writable boolean capability (child lock, light, options …)."""

    @property
    def is_on(self) -> bool | None:
        value = self.washer.get(self.spec.path)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.upper() in ("ON", "TRUE")
        return None

    async def _write(self, on: bool) -> None:
        value: Any = on
        current = self.washer.get(self.spec.path)
        if isinstance(current, str):
            value = "ON" if on else "OFF"
        await self.coordinator.async_send(self._appliance_id, generic.command(self.washer, self.spec.path, value))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self._write(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._write(False)

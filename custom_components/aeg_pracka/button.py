"""Start / pause / resume / stop buttons for the AEG / Electrolux washer."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry
from .entity import AegPrackaEntity

# translation key -> executeCommand value
BUTTONS: tuple[tuple[ButtonEntityDescription, str], ...] = (
    (ButtonEntityDescription(key="start", icon="mdi:play"), "START"),
    (ButtonEntityDescription(key="pauza", icon="mdi:pause"), "PAUSE"),
    (ButtonEntityDescription(key="pokracovat", icon="mdi:play-pause"), "RESUME"),
    (ButtonEntityDescription(key="stop", icon="mdi:stop"), "STOPRESET"),
    (ButtonEntityDescription(key="zapnut", icon="mdi:power-on"), "ON"),
    (ButtonEntityDescription(key="vypnut", icon="mdi:power-off"), "OFF"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AegButton(coordinator, appliance_id, desc, command)
        for appliance_id in coordinator.washers
        for desc, command in BUTTONS
    )


class AegButton(AegPrackaEntity, ButtonEntity):
    def __init__(self, coordinator, appliance_id: str, desc: ButtonEntityDescription, command: str) -> None:
        super().__init__(coordinator, appliance_id, desc.key)
        self.entity_description = desc
        self._command = command

    async def async_press(self) -> None:
        await self.coordinator.async_send(self._appliance_id, {"executeCommand": self._command})

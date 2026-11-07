"""Start / pause / resume / stop buttons for the AEG / Electrolux washer."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry
from . import generic
from .entity import AegPrackaEntity, GeneratedEntity

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
    entities: list[ButtonEntity] = []
    for appliance_id, w in coordinator.washers.items():
        allowed = set(w.capability_values("executeCommand"))
        if w.is_care:
            entities += [AegButton(coordinator, appliance_id, d, c) for d, c in BUTTONS if not allowed or c in allowed]
        entities += [GeneratedButton(coordinator, appliance_id, s) for s in generic.specs(w) if s.platform == "button"]
    async_add_entities(entities)


class AegButton(AegPrackaEntity, ButtonEntity):
    def __init__(self, coordinator, appliance_id: str, desc: ButtonEntityDescription, command: str) -> None:
        super().__init__(coordinator, appliance_id, desc.key)
        self.entity_description = desc
        self._command = command

    async def async_press(self) -> None:
        await self.coordinator.async_send(self._appliance_id, {"executeCommand": self._command})


class GeneratedButton(GeneratedEntity, ButtonEntity):
    """Writes one value of a write-only capability (e.g. executeCommand START)."""

    async def async_press(self) -> None:
        w = self.washer
        await self.coordinator.async_send(self._appliance_id, generic.command(w, self.spec.path, self.spec.command))

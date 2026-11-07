"""Binary sensors for the AEG / Electrolux washer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry
from .const import RUNNING_STATES
from .coordinator import Washer
from . import generic
from .entity import AegPrackaEntity, GeneratedEntity


def _upper(value) -> str | None:
    return None if value is None else str(value).upper()


@dataclass(frozen=True, kw_only=True)
class AegBinaryDescription(BinarySensorEntityDescription):
    value_fn: Callable[[Washer], bool | None]
    exists_fn: Callable[[Washer], bool] = lambda w: True


BINARY_SENSORS: tuple[AegBinaryDescription, ...] = (
    AegBinaryDescription(
        key="perie",
        exists_fn=lambda w: w.is_care,
        device_class=BinarySensorDeviceClass.RUNNING,
        value_fn=lambda w: None if w.state_key is None else w.state_key in RUNNING_STATES,
    ),
    AegBinaryDescription(
        key="doprate",
        exists_fn=lambda w: w.is_care,
        icon="mdi:check-circle-outline",
        value_fn=lambda w: None if w.state_key is None else w.state_key == "end_of_cycle",
    ),
    AegBinaryDescription(
        key="dvierka",
        exists_fn=lambda w: w.has("doorState"),
        device_class=BinarySensorDeviceClass.DOOR,
        value_fn=lambda w: None if (d := _upper(w.get("doorState"))) is None else d == "OPEN",
    ),
    AegBinaryDescription(
        key="zamok_dvierok",
        exists_fn=lambda w: w.has("doorLock"),
        device_class=BinarySensorDeviceClass.LOCK,
        # LOCK device class: on = unlocked.
        value_fn=lambda w: None if (d := _upper(w.get("doorLock"))) is None else d != "ON",
    ),
    AegBinaryDescription(
        key="pripojenie",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda w: w.connected,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[BinarySensorEntity] = []
    for appliance_id, w in coordinator.washers.items():
        entities += [AegBinarySensor(coordinator, appliance_id, d) for d in BINARY_SENSORS if d.exists_fn(w)]
        entities += [GeneratedBinarySensor(coordinator, appliance_id, s)
                     for s in generic.specs(w) if s.platform == "binary_sensor"]
    async_add_entities(entities)


class AegBinarySensor(AegPrackaEntity, BinarySensorEntity):
    entity_description: AegBinaryDescription

    def __init__(self, coordinator, appliance_id: str, desc: AegBinaryDescription) -> None:
        super().__init__(coordinator, appliance_id, desc.key)
        self.entity_description = desc

    @property
    def is_on(self) -> bool | None:
        return self.entity_description.value_fn(self.washer)

    @property
    def available(self) -> bool:
        # Connectivity must stay available to report "disconnected".
        if self.entity_description.key == "pripojenie":
            return self.coordinator.last_update_success
        return super().available


class GeneratedBinarySensor(GeneratedEntity, BinarySensorEntity):
    """Read-only on/off capability."""

    @property
    def is_on(self) -> bool | None:
        value = self.washer.get(self.spec.path)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.upper() in ("ON", "TRUE", "OPEN", "ENABLED", "1")
        return None

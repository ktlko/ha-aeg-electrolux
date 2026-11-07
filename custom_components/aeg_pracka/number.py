"""Numbers: oven target temperature plus every writable numeric capability."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry, generic
from .const import COOK_TYPES
from .entity import AegPrackaEntity, GeneratedEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[NumberEntity] = []
    for appliance_id, w in coordinator.washers.items():
        cap = w.capability("targetTemperatureC") or {}
        if w.type in COOK_TYPES and "write" in str(cap.get("access", "")):
            entities.append(OvenTemperature(coordinator, appliance_id))
        entities += [GeneratedNumber(coordinator, appliance_id, s) for s in generic.specs(w) if s.platform == "number"]
    async_add_entities(entities)


class OvenTemperature(AegPrackaEntity, NumberEntity):
    """Oven / steam oven target temperature."""

    _attr_device_class = NumberDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, appliance_id: str) -> None:
        super().__init__(coordinator, appliance_id, "rura_nastavit_teplotu")
        cap = coordinator.washers[appliance_id].capability("targetTemperatureC") or {}
        self._attr_native_min_value = float(cap.get("min", 30))
        self._attr_native_max_value = float(cap.get("max", 300))
        self._attr_native_step = float(cap.get("step", 5))

    @property
    def native_value(self) -> float | None:
        v = self.washer.get("targetTemperatureC")
        return float(v) if isinstance(v, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_send(self._appliance_id, {"targetTemperatureC": value})


class GeneratedNumber(GeneratedEntity, NumberEntity):
    """Writable numeric capability with a range."""

    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, appliance_id: str, spec) -> None:
        super().__init__(coordinator, appliance_id, spec)
        self._attr_native_min_value = spec.minimum
        self._attr_native_max_value = spec.maximum
        self._attr_native_step = spec.step
        if spec.unit == "°C":
            self._attr_device_class = NumberDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif spec.unit == "s":
            self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        elif spec.unit:
            self._attr_native_unit_of_measurement = spec.unit

    @property
    def native_value(self) -> float | None:
        v = self.washer.get(self.spec.path)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    async def async_set_native_value(self, value: float) -> None:
        payload_value = int(value) if float(self.spec.step or 1).is_integer() else value
        await self.coordinator.async_send(
            self._appliance_id, generic.command(self.washer, self.spec.path, payload_value)
        )

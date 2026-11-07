"""Sensors for the AEG / Electrolux washer."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfMass, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import AegPrackaConfigEntry
from .const import (
    APPLIANCE_STATES,
    CYCLE_PHASES,
    COOK_TYPES,
    RUNNING_STATES,
    state_key,
)
from .coordinator import Washer
from . import generic
from .entity import AegPrackaEntity, GeneratedEntity


LINK_QUALITY = ("excellent", "very_good", "good", "fair", "poor", "very_poor")


def _minutes(w: Washer) -> int | None:
    if w.state_key not in RUNNING_STATES:
        return 0
    sec = w.get("timeToEnd")
    if not isinstance(sec, (int, float)) or sec < 0:
        return None
    return round(sec / 60)


def _end_time(w: Washer) -> datetime | None:
    sec = w.get("timeToEnd")
    if w.state_key not in RUNNING_STATES or not isinstance(sec, (int, float)) or sec <= 0:
        return None
    # Round to the minute so the state doesn't change on every SSE tick.
    end = dt_util.utcnow() + timedelta(seconds=sec)
    return end.replace(second=0, microsecond=0)


def _phase(w: Washer) -> str | None:
    raw = w.get("cyclePhase")
    if raw is None:
        return None
    return CYCLE_PHASES.get(raw, "none" if w.state_key not in RUNNING_STATES else "other")


def _alerts(w: Washer) -> int:
    alerts = w.get("alerts") or []
    return len(alerts) if isinstance(alerts, list) else 0


def _total_hours(w: Washer) -> float | None:
    seconds = w.get("applianceTotalWorkingTime")
    return round(seconds / 3600) if isinstance(seconds, (int, float)) else None


def _load_kg(w: Washer) -> float | None:
    """Measured load in kg; 65535 means 'not measured yet'."""
    for key in ("measuredLoadWeight", "fcOptisenseLoadWeight"):
        grams = w.get(key)
        if isinstance(grams, (int, float)) and 0 < grams < 65535:
            return round(grams / 1000, 1)
    return None


@dataclass(frozen=True, kw_only=True)
class AegSensorDescription(SensorEntityDescription):
    value_fn: Callable[[Washer], Any]
    attrs_fn: Callable[[Washer], dict[str, Any]] | None = None
    options_prop: str | None = None  # options come from the washer's capabilities
    exists_fn: Callable[[Washer], bool] = lambda w: True


SENSORS: tuple[AegSensorDescription, ...] = (
    AegSensorDescription(
        key="stav",
        exists_fn=lambda w: w.has("applianceState"),
        device_class=SensorDeviceClass.ENUM,
        options=sorted({*APPLIANCE_STATES.values(), "other"}),
        value_fn=lambda w: (k if (k := w.state_key) in APPLIANCE_STATES.values() else ("other" if k else None)),
        attrs_fn=lambda w: {"raw": w.get("applianceState")},
    ),
    AegSensorDescription(
        key="program",
        exists_fn=lambda w: w.has("userSelections/programUID"),
        icon="mdi:tshirt-crew",
        device_class=SensorDeviceClass.ENUM,
        options_prop="programUID",
        value_fn=lambda w: state_key(w.get("userSelections/programUID")),
        attrs_fn=lambda w: {"uid": w.get("userSelections/programUID")},
    ),
    AegSensorDescription(
        key="faza",
        exists_fn=lambda w: w.has("cyclePhase"),
        device_class=SensorDeviceClass.ENUM,
        options=sorted({*CYCLE_PHASES.values(), "other"}),
        value_fn=_phase,
        attrs_fn=lambda w: {"raw": w.get("cyclePhase"), "subphase": w.get("cycleSubPhase")},
    ),
    AegSensorDescription(
        key="zostava",
        exists_fn=lambda w: w.has("timeToEnd"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-sand",
        value_fn=_minutes,
    ),
    AegSensorDescription(
        key="koniec",
        exists_fn=lambda w: w.has("timeToEnd"),
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
        value_fn=_end_time,
    ),
    AegSensorDescription(
        key="priebeh",
        exists_fn=lambda w: w.has("timeToEnd") and w.type not in COOK_TYPES,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:progress-clock",
        value_fn=lambda w: w.progress,
    ),
    AegSensorDescription(
        key="teplota",
        exists_fn=lambda w: w.has("userSelections/analogTemperature"),
        icon="mdi:thermometer-water",
        device_class=SensorDeviceClass.ENUM,
        options_prop="analogTemperature",
        value_fn=lambda w: state_key(w.get("userSelections/analogTemperature")),
    ),
    AegSensorDescription(
        key="odstredovanie",
        exists_fn=lambda w: w.has("userSelections/analogSpinSpeed"),
        icon="mdi:rotate-right",
        device_class=SensorDeviceClass.ENUM,
        options_prop="analogSpinSpeed",
        value_fn=lambda w: state_key(w.get("userSelections/analogSpinSpeed")),
    ),
    AegSensorDescription(
        key="napln",
        exists_fn=lambda w: w.has("measuredLoadWeight") or w.has("fcOptisenseLoadWeight"),
        icon="mdi:weight-kilogram",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        value_fn=_load_kg,
    ),
    AegSensorDescription(
        key="tvrdost_vody",
        exists_fn=lambda w: w.has("waterHardness"),
        icon="mdi:water-opacity",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda w: (
            int(h.removeprefix("STEP_"))
            if isinstance(h := w.get("waterHardness"), str) and h.removeprefix("STEP_").isdigit()
            else None
        ),
    ),
    AegSensorDescription(
        key="signal",
        exists_fn=lambda w: w.has("networkInterface/linkQualityIndicator"),
        icon="mdi:wifi",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.ENUM,
        options=[*LINK_QUALITY, "undefined"],
        value_fn=lambda w: (
            k if (k := state_key(w.get("networkInterface/linkQualityIndicator"))) in LINK_QUALITY
            else ("undefined" if k else None)
        ),
    ),
    AegSensorDescription(
        key="pocet_cyklov",
        exists_fn=lambda w: w.has("totalCycleCounter"),
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda w: w.get("totalCycleCounter"),
    ),
    AegSensorDescription(
        key="odpracovane",
        exists_fn=lambda w: w.has("applianceTotalWorkingTime"),
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_total_hours,
    ),
    AegSensorDescription(
        key="upozornenia",
        exists_fn=lambda w: w.has("alerts"),
        icon="mdi:alert-circle-outline",
        value_fn=_alerts,
        attrs_fn=lambda w: {"alerts": w.get("alerts") or []},
    ),
    AegSensorDescription(
        key="dialkove_ovladanie",
        exists_fn=lambda w: w.has("remoteControl"),
        icon="mdi:remote",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.ENUM,
        options=["enabled", "disabled"],
        value_fn=lambda w: (
            None if (r := w.get("remoteControl")) is None else ("enabled" if "ENABLED" in str(r).upper() else "disabled")
        ),
        attrs_fn=lambda w: {"raw": w.get("remoteControl")},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[SensorEntity] = []
    for appliance_id, w in coordinator.washers.items():
        entities += [AegSensor(coordinator, appliance_id, d) for d in SENSORS if d.exists_fn(w)]
        entities += [AegSensor(coordinator, appliance_id, d) for d in COOK_SENSORS if w.type in COOK_TYPES and d.exists_fn(w)]
        entities += [GeneratedSensor(coordinator, appliance_id, s) for s in generic.specs(w) if s.platform == "sensor"]
    async_add_entities(entities)


class AegSensor(AegPrackaEntity, SensorEntity):
    entity_description: AegSensorDescription

    def __init__(self, coordinator, appliance_id: str, desc: AegSensorDescription) -> None:
        super().__init__(coordinator, appliance_id, desc.key)
        self.entity_description = desc

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.washer)

    @property
    def options(self) -> list[str] | None:
        prop = self.entity_description.options_prop
        if prop is None:
            return self.entity_description.options
        keys = [k for v in self.washer.capability_values(f"userSelections/{prop}") if (k := state_key(v))]
        if (current := self.native_value) and current not in keys:
            keys.append(current)
        return keys

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attrs_fn is None:
            return None
        return self.entity_description.attrs_fn(self.washer)


def _c(w: Washer, path: str) -> float | None:
    v = w.get(path)
    return round(float(v), 1) if isinstance(v, (int, float)) and v > -100 else None


def _seconds_to_min(w: Washer, path: str) -> int | None:
    v = w.get(path)
    return round(v / 60) if isinstance(v, (int, float)) and v >= 0 else None


COOK_SENSORS: tuple[AegSensorDescription, ...] = (
    AegSensorDescription(
        key="rura_program",
        icon="mdi:stove",
        device_class=SensorDeviceClass.ENUM,
        options_prop="program",
        exists_fn=lambda w: w.has("program"),
        value_fn=lambda w: state_key(w.get("program")),
    ),
    AegSensorDescription(
        key="rura_teplota",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        exists_fn=lambda w: w.has("displayTemperatureC"),
        value_fn=lambda w: _c(w, "displayTemperatureC"),
    ),
    AegSensorDescription(
        key="rura_ciel",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        exists_fn=lambda w: w.has("targetTemperatureC"),
        value_fn=lambda w: _c(w, "targetTemperatureC"),
    ),
    AegSensorDescription(
        key="sonda",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        exists_fn=lambda w: w.has("displayFoodProbeTemperatureC"),
        value_fn=lambda w: _c(w, "displayFoodProbeTemperatureC") if w.get("foodProbeInsertionState") != "NOT_INSERTED" else None,
    ),
    AegSensorDescription(
        key="cas_behu",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        exists_fn=lambda w: w.has("runningTime"),
        value_fn=lambda w: _seconds_to_min(w, "runningTime"),
    ),
)


class GeneratedSensor(GeneratedEntity, SensorEntity):
    """Read-only capability."""

    def __init__(self, coordinator, appliance_id: str, spec) -> None:
        super().__init__(coordinator, appliance_id, spec)
        if spec.kind == "string":
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = [v.lower() for v in spec.options]
        elif spec.unit == "°C":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        elif spec.unit == "s":
            self._attr_device_class = SensorDeviceClass.DURATION
            self._attr_native_unit_of_measurement = UnitOfTime.SECONDS
        elif spec.unit:
            self._attr_native_unit_of_measurement = spec.unit

    @property
    def native_value(self) -> Any:
        value = self.washer.get(self.spec.path)
        if self.spec.kind == "string":
            key = state_key(value) if isinstance(value, str) else None
            return key if key in (self._attr_options or []) else None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return None
        if self.spec.unit == "s" and value < 0:
            return None
        return value

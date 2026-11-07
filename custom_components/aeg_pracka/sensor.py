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
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfMass, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import AegPrackaConfigEntry
from .const import (
    APPLIANCE_STATES,
    CYCLE_PHASES,
    RUNNING_STATES,
    state_key,
)
from .coordinator import Washer
from .entity import AegPrackaEntity


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


SENSORS: tuple[AegSensorDescription, ...] = (
    AegSensorDescription(
        key="stav",
        device_class=SensorDeviceClass.ENUM,
        options=sorted(set(APPLIANCE_STATES.values())),
        value_fn=lambda w: w.state_key,
        attrs_fn=lambda w: {"raw": w.get("applianceState")},
    ),
    AegSensorDescription(
        key="program",
        icon="mdi:tshirt-crew",
        device_class=SensorDeviceClass.ENUM,
        options_prop="programUID",
        value_fn=lambda w: state_key(w.get("userSelections/programUID")),
        attrs_fn=lambda w: {"uid": w.get("userSelections/programUID")},
    ),
    AegSensorDescription(
        key="faza",
        device_class=SensorDeviceClass.ENUM,
        options=sorted({*CYCLE_PHASES.values(), "other"}),
        value_fn=_phase,
        attrs_fn=lambda w: {"raw": w.get("cyclePhase"), "subphase": w.get("cycleSubPhase")},
    ),
    AegSensorDescription(
        key="zostava",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:timer-sand",
        value_fn=_minutes,
    ),
    AegSensorDescription(
        key="koniec",
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock-end",
        value_fn=_end_time,
    ),
    AegSensorDescription(
        key="priebeh",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:progress-clock",
        value_fn=lambda w: w.progress,
    ),
    AegSensorDescription(
        key="teplota",
        icon="mdi:thermometer-water",
        device_class=SensorDeviceClass.ENUM,
        options_prop="analogTemperature",
        value_fn=lambda w: state_key(w.get("userSelections/analogTemperature")),
    ),
    AegSensorDescription(
        key="odstredovanie",
        icon="mdi:rotate-right",
        device_class=SensorDeviceClass.ENUM,
        options_prop="analogSpinSpeed",
        value_fn=lambda w: state_key(w.get("userSelections/analogSpinSpeed")),
    ),
    AegSensorDescription(
        key="napln",
        icon="mdi:weight-kilogram",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement=UnitOfMass.KILOGRAMS,
        value_fn=_load_kg,
    ),
    AegSensorDescription(
        key="tvrdost_vody",
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
        icon="mdi:counter",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda w: w.get("totalCycleCounter"),
    ),
    AegSensorDescription(
        key="odpracovane",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_total_hours,
    ),
    AegSensorDescription(
        key="upozornenia",
        icon="mdi:alert-circle-outline",
        value_fn=_alerts,
        attrs_fn=lambda w: {"alerts": w.get("alerts") or []},
    ),
    AegSensorDescription(
        key="dialkove_ovladanie",
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
    async_add_entities(
        AegSensor(coordinator, appliance_id, desc)
        for appliance_id in coordinator.washers
        for desc in SENSORS
    )


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

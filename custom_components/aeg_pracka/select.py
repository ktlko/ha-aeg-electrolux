"""Program / temperature / spin selects for the AEG / Electrolux washer."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import AegPrackaConfigEntry
from .const import state_key
from .coordinator import Washer
from . import generic
from .entity import AegPrackaEntity, GeneratedEntity


@dataclass(frozen=True, kw_only=True)
class AegSelectDescription(SelectEntityDescription):
    prop: str  # property inside userSelections


SELECTS: tuple[AegSelectDescription, ...] = (
    AegSelectDescription(key="vyber_programu", icon="mdi:tshirt-crew", prop="programUID"),
    AegSelectDescription(key="vyber_teploty", icon="mdi:thermometer-water", prop="analogTemperature"),
    AegSelectDescription(key="vyber_otacok", icon="mdi:rotate-right", prop="analogSpinSpeed"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: AegPrackaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        AegSelect(coordinator, appliance_id, desc)
        for appliance_id in coordinator.washers
        for desc in SELECTS
        if coordinator.washers[appliance_id].capability_values(f"userSelections/{desc.prop}")
    )
    async_add_entities(
        GeneratedSelect(coordinator, appliance_id, s)
        for appliance_id, w in coordinator.washers.items()
        for s in generic.specs(w)
        if s.platform == "select"
    )


class AegSelect(AegPrackaEntity, SelectEntity):
    entity_description: AegSelectDescription

    def __init__(self, coordinator, appliance_id: str, desc: AegSelectDescription) -> None:
        super().__init__(coordinator, appliance_id, desc.key)
        self.entity_description = desc

    def _raw_values(self) -> list[str]:
        w: Washer = self.washer
        if self.entity_description.prop == "programUID":
            return w.capability_values("userSelections/programUID")
        # Temperatures / spin speeds depend on the selected program.
        program = w.get("userSelections/programUID")
        prog_cap = (
            (w.details.capabilities.get("userSelections/programUID", {}) if w.details else {})
            .get("values", {})
            .get(program, {})
        )
        per_program = prog_cap.get(f"userSelections/{self.entity_description.prop}", {})
        values = per_program.get("values") if isinstance(per_program, dict) else None
        if values:
            return [v for v in values if v != "DISABLED"]
        return w.capability_values(f"userSelections/{self.entity_description.prop}")

    def _label(self, raw: str) -> str:
        return state_key(raw) or raw

    @property
    def options(self) -> list[str]:
        labels = [self._label(v) for v in self._raw_values()]
        current = self.current_option
        if current and current not in labels:
            labels.append(current)
        return labels

    @property
    def current_option(self) -> str | None:
        raw = self.washer.get(f"userSelections/{self.entity_description.prop}")
        return self._label(raw) if raw else None

    async def async_select_option(self, option: str) -> None:
        raw = next((v for v in self._raw_values() if self._label(v) == option), option)
        selections: dict[str, str] = {self.entity_description.prop: raw}
        if self.entity_description.prop != "programUID":
            # The API requires the program alongside temperature / spin changes.
            selections["programUID"] = self.washer.get("userSelections/programUID")
        await self.coordinator.async_send(self._appliance_id, {"userSelections": selections})


class GeneratedSelect(GeneratedEntity, SelectEntity):
    """Writable capability with a list of values."""

    def __init__(self, coordinator, appliance_id: str, spec) -> None:
        super().__init__(coordinator, appliance_id, spec)
        self._map: dict[str, str] = {}
        for v in spec.options:
            name = generic.label(spec.path, v)
            self._map[name if name not in self._map else f"{name} ({v.lower()})"] = v
        self._attr_options = list(self._map)

    @property
    def current_option(self) -> str | None:
        value = self.washer.get(self.spec.path)
        return next((k for k, v in self._map.items() if v == value), None)

    async def async_select_option(self, option: str) -> None:
        w = self.washer
        await self.coordinator.async_send(self._appliance_id, generic.command(w, self.spec.path, self._map[option]))

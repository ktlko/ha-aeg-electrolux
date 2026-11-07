"""Base entity for the AEG / Electrolux washer."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AegPrackaCoordinator, Washer


class AegPrackaEntity(CoordinatorEntity[AegPrackaCoordinator]):
    """Entity bound to one washer."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AegPrackaCoordinator, appliance_id: str, key: str) -> None:
        super().__init__(coordinator)
        self._appliance_id = appliance_id
        self._attr_translation_key = key
        self._attr_unique_id = f"{appliance_id}_{key}"
        washer = coordinator.washers[appliance_id]
        info = washer.details.applianceInfo if washer.details else None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, appliance_id)},
            name=washer.appliance.applianceName or "Washer",
            manufacturer=info.brand if info else "AEG",
            model=info.model if info and info.model else None,
            model_id=info.pnc if info else None,
            serial_number=info.serialNumber if info else None,
        )

    @property
    def washer(self) -> Washer:
        return self.coordinator.washers[self._appliance_id]

    @property
    def available(self) -> bool:
        return super().available and self.washer.state is not None

"""Diagnostics for the AEG / Electrolux washer (tokens redacted)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import AegPrackaConfigEntry
from .const import CONF_ACCESS_TOKEN, CONF_API_KEY, CONF_REFRESH_TOKEN

TO_REDACT = {CONF_API_KEY, CONF_ACCESS_TOKEN, CONF_REFRESH_TOKEN, "serialNumber", "applianceId"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AegPrackaConfigEntry
) -> dict[str, Any]:
    coordinator = entry.runtime_data
    return {
        "entry": async_redact_data(dict(entry.data), TO_REDACT),
        "washers": [
            {
                "appliance": async_redact_data(w.appliance.model_dump(mode="json"), TO_REDACT),
                "details": async_redact_data(w.details.model_dump(mode="json"), TO_REDACT)
                if w.details
                else None,
                "reported": w.reported,
                "cycle_total": w.cycle_total,
            }
            for w in coordinator.washers.values()
        ],
    }

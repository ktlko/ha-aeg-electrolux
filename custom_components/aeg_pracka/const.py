"""Constants for the AEG / Electrolux washer integration."""

from datetime import timedelta

DOMAIN = "aeg_pracka"

CONF_API_KEY = "api_key"
CONF_ACCESS_TOKEN = "access_token"
CONF_REFRESH_TOKEN = "refresh_token"

# Safety-net poll; live updates come from the SSE stream.
SCAN_INTERVAL = timedelta(minutes=5)

# Appliance families. Care = laundry and dish care with programmes and cycles.
CARE_TYPES = ("WM", "WD", "TD", "DW")
COOK_TYPES = ("OV", "SO")
# Types confirmed on real hardware; everything else is labelled untested.
TESTED_TYPES = ("WM",)

CARD_URL = "/aeg_pracka/aeg-pracka-card.js"

# Raw appliance states -> stable lowercase keys used by the enum sensor.
APPLIANCE_STATES = {
    "OFF": "off",
    "IDLE": "idle",
    "READY_TO_START": "ready_to_start",
    "DELAYED_START": "delayed_start",
    "RUNNING": "running",
    "PAUSED": "paused",
    "END_OF_CYCLE": "end_of_cycle",
    "ALARM": "alarm",
    "ON": "on",
    "STANDBY": "idle",
}

RUNNING_STATES = ("running", "paused", "delayed_start")

CYCLE_PHASES = {
    "UNAVAILABLE": "none",
    "WASH": "wash",
    "PREWASH": "prewash",
    "RINSE": "rinse",
    "SPIN": "spin",
    "DRY": "dry",
    "STEAM": "steam",
    "ANTICREASE": "anticrease",
    "COOLDOWN": "cooldown",
    "SOAK": "soak",
}

# Service programs the washer lists but that make no sense to pick.
HIDDEN_PROGRAMS = ("MACHINE_SETTINGS_HIDDEN_TEST",)


def state_key(raw: str | None) -> str | None:
    """Raw API value -> translation key ('COTTON_PR_COTTONS' -> 'cotton_pr_cottons')."""
    return raw.lower() if isinstance(raw, str) and raw else None

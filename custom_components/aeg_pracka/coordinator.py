"""Data coordinator: REST polling + Electrolux SSE live stream."""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from typing import Any

from electrolux_group_developer_sdk.auth.token_manager import TokenManager
from electrolux_group_developer_sdk.client.appliance_client import (
    ApplianceClient,
    apply_sse_update,
)
from electrolux_group_developer_sdk.client.dto.appliance import Appliance
from electrolux_group_developer_sdk.client.dto.appliance_details import ApplianceDetails
from electrolux_group_developer_sdk.client.dto.appliance_state import ApplianceState

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    APPLIANCE_STATES,
    CONF_ACCESS_TOKEN,
    CONF_API_KEY,
    CONF_REFRESH_TOKEN,
    DOMAIN,
    HIDDEN_PROGRAMS,
    RUNNING_STATES,
    SCAN_INTERVAL,
    WASHER_TYPES,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class Washer:
    """One washer: static info plus the latest state."""

    appliance: Appliance
    details: ApplianceDetails | None
    state: ApplianceState | None
    # Longest timeToEnd seen in the current cycle, used for the progress %.
    cycle_total: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def reported(self) -> dict[str, Any]:
        if self.state is None:
            return {}
        return self.state.properties.get("reported", {}) or {}

    def get(self, path: str, default: Any = None) -> Any:
        """Read a reported property by 'a/b/c' path."""
        node: Any = self.reported
        for key in path.split("/"):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    @property
    def state_key(self) -> str | None:
        raw = self.get("applianceState")
        return APPLIANCE_STATES.get(raw, raw.lower() if isinstance(raw, str) else None)

    @property
    def connected(self) -> bool:
        if self.state is None:
            return False
        conn = self.state.connectionState or self.get("connectivityState") or ""
        return str(conn).lower() == "connected"

    def capability_values(self, path: str) -> list[str]:
        """Allowed values for a capability (e.g. 'userSelections/programUID')."""
        if self.details is None:
            return []
        cap = self.details.capabilities.get(path)
        if cap is None:
            # Capabilities can also be nested.
            node: Any = self.details.capabilities
            for key in path.split("/"):
                node = node.get(key, {}) if isinstance(node, dict) else {}
            cap = node
        values = cap.get("values", {}) if isinstance(cap, dict) else {}
        return [
            k
            for k, meta in values.items()
            if k != "DISABLED"
            and k not in HIDDEN_PROGRAMS
            and not (isinstance(meta, dict) and meta.get("disabled"))
        ]

    def track_cycle(self) -> None:
        """Remember the cycle length so progress can be computed."""
        remaining = self.get("timeToEnd")
        if self.state_key in RUNNING_STATES and isinstance(remaining, (int, float)):
            if remaining > self.cycle_total:
                self.cycle_total = int(remaining)
        elif self.state_key in ("idle", "off", "ready_to_start"):
            self.cycle_total = 0

    @property
    def progress(self) -> int | None:
        if self.state_key == "end_of_cycle":
            return 100
        remaining = self.get("timeToEnd")
        if self.state_key not in RUNNING_STATES or not self.cycle_total:
            return 0 if self.state_key else None
        if not isinstance(remaining, (int, float)):
            return None
        done = (self.cycle_total - remaining) / self.cycle_total * 100
        return max(0, min(100, round(done)))


class AegPrackaCoordinator(DataUpdateCoordinator[dict[str, Washer]]):
    """Keeps all washers of one Electrolux account up to date."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self._token_manager = TokenManager(
            access_token=entry.data[CONF_ACCESS_TOKEN],
            refresh_token=entry.data[CONF_REFRESH_TOKEN],
            api_key=entry.data[CONF_API_KEY],
            on_token_update=self._on_token_update,
        )
        self.client = ApplianceClient(
            self._token_manager, external_user_agent="HomeAssistant-aeg_pracka"
        )
        self.washers: dict[str, Washer] = {}

    @callback
    def _on_token_update(self, access_token: str, refresh_token: str, api_key: str) -> None:
        """Persist rotated tokens, otherwise the next restart would fail."""
        entry = self.config_entry
        if (
            entry.data.get(CONF_ACCESS_TOKEN) == access_token
            and entry.data.get(CONF_REFRESH_TOKEN) == refresh_token
        ):
            return
        self.hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF_ACCESS_TOKEN: access_token,
                CONF_REFRESH_TOKEN: refresh_token,
                CONF_API_KEY: api_key,
            },
        )

    async def async_discover(self) -> None:
        """Find washers on the account (run once on setup)."""
        try:
            appliances = await self.client.get_appliances()
        except Exception as err:  # SDK wraps everything in its own exceptions
            if getattr(err, "status", None) in (401, 403):
                raise ConfigEntryAuthFailed("Electrolux rejected the credentials") from err
            raise UpdateFailed(f"Cannot list appliances: {err}") from err

        for appliance in appliances:
            if appliance.applianceType not in WASHER_TYPES:
                continue
            try:
                details = await self.client.get_appliance_details(appliance.applianceId)
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning("Details for %s not loaded: %s", appliance.applianceName, err)
                details = None
            self.washers[appliance.applianceId] = Washer(appliance, details, None)

        if not self.washers:
            _LOGGER.warning("No washer found on the Electrolux account")

    async def _async_update_data(self) -> dict[str, Washer]:
        for appliance_id, washer in self.washers.items():
            try:
                washer.state = await self.client.get_appliance_state(appliance_id)
            except Exception as err:
                if getattr(err, "status", None) in (401, 403):
                    raise ConfigEntryAuthFailed("Electrolux rejected the credentials") from err
                raise UpdateFailed(f"Cannot read washer state: {err}") from err
            washer.track_cycle()
        return self.washers

    # ---- live stream -------------------------------------------------------

    def start_stream(self) -> None:
        """Run the SSE stream for the lifetime of the config entry."""
        for appliance_id in self.washers:
            self.client.add_listener(appliance_id, self._make_listener(appliance_id))

        async def _resync() -> None:
            await self.async_request_refresh()

        self.config_entry.async_create_background_task(
            self.hass,
            self.client.start_event_stream(do_on_livestream_opening_list=[_resync]),
            name=f"{DOMAIN}_sse",
        )

    def _make_listener(self, appliance_id: str):
        @callback
        def _listener(event: dict[str, Any]) -> None:
            washer = self.washers.get(appliance_id)
            if washer is None or washer.state is None:
                return
            washer.state = apply_sse_update(washer.state, event)
            washer.track_cycle()
            self.async_set_updated_data(self.washers)

        return _listener

    # ---- commands ----------------------------------------------------------

    async def async_send(self, appliance_id: str, command: dict[str, Any]) -> None:
        """Send a command and refresh the state."""
        washer = self.washers[appliance_id]
        remote = str(washer.get("remoteControl", "")).upper()
        if remote and "ENABLED" not in remote:
            raise HomeAssistantError(translation_domain=DOMAIN, translation_key="remote_disabled")
        try:
            await self.client.send_command(appliance_id, command)
        except Exception as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="command_failed",
                translation_placeholders={"error": str(err)},
            ) from err
        await self.async_request_refresh()

"""Config flow for the AEG / Electrolux washer."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from electrolux_group_developer_sdk.auth.token_manager import (
    TokenManager,
    get_user_id_from_token,
)
from electrolux_group_developer_sdk.client.appliance_client import ApplianceClient
from electrolux_group_developer_sdk.client.bad_credentials_exception import (
    BadCredentialsException,
)
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from .const import CONF_ACCESS_TOKEN, CONF_API_KEY, CONF_REFRESH_TOKEN, DOMAIN

_SECRET = TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD))

SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): _SECRET,
        vol.Required(CONF_ACCESS_TOKEN): _SECRET,
        vol.Required(CONF_REFRESH_TOKEN): _SECRET,
    }
)


async def _validate(data: dict[str, Any]) -> tuple[str, dict[str, str]]:
    """Test credentials; return (user_id, possibly refreshed tokens)."""
    tokens = dict(data)

    def _store(access: str, refresh: str, api_key: str) -> None:
        tokens.update({CONF_ACCESS_TOKEN: access, CONF_REFRESH_TOKEN: refresh, CONF_API_KEY: api_key})

    manager = TokenManager(
        access_token=data[CONF_ACCESS_TOKEN].strip(),
        refresh_token=data[CONF_REFRESH_TOKEN].strip(),
        api_key=data[CONF_API_KEY].strip(),
        on_token_update=_store,
    )
    await ApplianceClient(manager).test_connection()
    return get_user_id_from_token(tokens[CONF_ACCESS_TOKEN]), tokens


class AegPrackaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Ask for the three Electrolux developer-portal values."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                user_id, tokens = await _validate(user_input)
            except BadCredentialsException:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="AEG / Electrolux", data=tokens)
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)

    async def async_step_reauth(self, entry_data: Mapping[str, Any]) -> ConfigFlowResult:
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                user_id, tokens = await _validate(user_input)
            except BadCredentialsException:
                errors["base"] = "invalid_auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_mismatch()
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(), data_updates=tokens
                )
        return self.async_show_form(step_id="reauth_confirm", data_schema=SCHEMA, errors=errors)

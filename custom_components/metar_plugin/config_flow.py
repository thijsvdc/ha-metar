"""Config flow for METAR integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_STATION, DOMAIN

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_STATION): str,
    }
)

class MetarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if station ID is already configured
            await self.async_set_unique_id(user_input[CONF_STATION].upper())
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=user_input[CONF_STATION].upper(),
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MetarOptionsFlow:
        """Get the options flow for this handler."""
        return MetarOptionsFlow(config_entry)

class MetarOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for METAR integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_STATION,
                        default=self.config_entry.options.get(
                            CONF_STATION, self.config_entry.data[CONF_STATION]
                        ),
                    ): str,
                }
            ),
        )

from homeassistant import config_entries
import voluptuous as vol
import logging

from .const import DOMAIN

LOGGER = logging.getLogger(__name__)

LOGGER.info("METAR Plugin: Starting setup...")

class MetarPluginConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR Plugin."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"METAR: {user_input['icao']}",
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("icao", default="EBBR"): str
            })
        )

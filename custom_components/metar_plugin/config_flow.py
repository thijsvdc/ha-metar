from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

class MetarPluginConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR Plugin."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title=f"METAR: {user_input['icao']}", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("icao", default="KJFK"): str,  # Default ICAO code
            }),
        )

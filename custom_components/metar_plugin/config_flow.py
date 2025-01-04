from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN

@config_entries.HANDLERS.register(DOMAIN)
class MetarPluginConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR Plugin."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(title="METAR Plugin", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required("icao"): str}),
        )


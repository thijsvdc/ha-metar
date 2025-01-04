import voluptuous as vol
from homeassistant import config_entries

from .const import DOMAIN  # Replace with your domain constant

class MetarPluginConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for METAR Plugin."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate the ICAO code here if needed
            return self.async_create_entry(title=user_input["icao"], data=user_input)

        # Show the config form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required("icao", default="KJFK"): str}
            ),
            errors=errors,
        )

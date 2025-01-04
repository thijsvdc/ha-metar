from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from .const import DOMAIN
import logging

LOGGER = logging.getLogger(__name__)

LOGGER.info("METAR Plugin: Starting setup...")

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the METAR Plugin integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up METAR Plugin from a config entry."""
    icao = entry.data["icao"]

    # Store the configuration in domain data
    hass.data[DOMAIN][entry.entry_id] = icao

    # Set up the sensor platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")

async def async_setup_entry(hass, entry):
    """Set up METAR Plugin from a config entry."""
    icao = entry.data["icao"]
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = icao
    return True

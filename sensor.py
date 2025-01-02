import requests
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "metar_plugin"
DEFAULT_UPDATE_INTERVAL = 10  # Minutes

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the METAR plugin based on a config entry."""
    icao_code = config_entry.data.get("icao_code")
    update_interval = config_entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)

    coordinator = MetarDataUpdateCoordinator(hass, icao_code, update_interval)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([MetarSensor(coordinator)])

class MetarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching METAR data from the API."""

    def __init__(self, hass, icao_code, update_interval):
        """Initialize the coordinator."""
        self.icao_code = icao_code
        self.api_url = f"https://tgftp.nws.noaa.gov/data/observations/metar/stations/{icao_code.upper()}.TXT"
        
        super().__init__(
            hass,
            _LOGGER,
            name="METAR Data Coordinator",
            update_interval=timedelta(minutes=update_interval),
        )

    async def _async_update_data(self):
        """Fetch data from the METAR API."""
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.text
            return self._parse_metar(data)
        except requests.RequestException as e:
            raise UpdateFailed(f"Error fetching METAR data: {e}")

    def _parse_metar(self, raw_data):
        """Parse raw METAR data."""
        lines = raw_data.strip().splitlines()
        return lines[-1] if lines else None

class MetarSensor(SensorEntity):
    """Representation of a METAR sensor."""

    def __init__(self, coordinator):
        """Initialize the METAR sensor."""
        self.coordinator = coordinator

    @property
    def name(self):
        return f"METAR {self.coordinator.icao_code}"

    @property
    def state(self):
        return self.coordinator.data

    @property
    def unique_id(self):
        return f"metar_{self.coordinator.icao_code}"

    @property
    def available(self):
        return self.coordinator.last_update_success

    async def async_update(self):
        """Update the sensor."""
        await self.coordinator.async_request_refresh()

    @property
    def extra_state_attributes(self):
        return {
            "icao_code": self.coordinator.icao_code,
        }

# Configuration flow and other setup components would be handled as per HACS requirements.

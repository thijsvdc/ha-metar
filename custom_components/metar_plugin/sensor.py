"""Support for METAR weather service."""
from datetime import datetime
import logging
from typing import Any

from aiohttp import ClientError
import voluptuous as vol
from metar import Metar

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_CLOUDS,
    ATTR_DEWPOINT,
    ATTR_LAST_UPDATE,
    ATTR_PRESSURE,
    ATTR_STATION,
    ATTR_TEMPERATURE,
    ATTR_VISIBILITY,
    ATTR_WEATHER,
    ATTR_WIND,
    CONF_STATION,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

METAR_BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations"

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the METAR sensor."""
    station = config_entry.data[CONF_STATION]
    
    coordinator = MetarDataUpdateCoordinator(
        hass,
        station=station,
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([MetarSensor(coordinator, station)], True)

class MetarDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching METAR data."""

    def __init__(
        self,
        hass: HomeAssistant,
        station: str,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )
        self.station = station
        self.session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from METAR."""
        try:
            url = f"{METAR_BASE_URL}/{self.station}.TXT"
            async with self.session.get(url) as response:
                text = await response.text()
                if response.status != 200:
                    _LOGGER.error(
                        "Error retrieving METAR data: %s", response.status
                    )
                    return None

            lines = text.splitlines()
            if len(lines) < 2:
                _LOGGER.error("METAR data has wrong format")
                return None

            metar_data = lines[1]
            obs = Metar.Metar(metar_data)

            data = {
                ATTR_STATION: obs.station_id,
                ATTR_LAST_UPDATE: obs.time,
                ATTR_TEMPERATURE: obs.temp.value("C") if obs.temp else None,
                ATTR_DEWPOINT: obs.dewpt.value("C") if obs.dewpt else None,
                ATTR_WIND: f"{obs.wind_speed.value('KMH')} km/h from {obs.wind_dir.compass() if obs.wind_dir else 'Unknown'}" if obs.wind_speed else "Calm",
                ATTR_VISIBILITY: f"{obs.vis.value('KM')} km" if obs.vis else None,
                ATTR_PRESSURE: f"{obs.press.value('HPA')} hPa" if obs.press else None,
                ATTR_WEATHER: str(obs.present_weather()) if obs.present_weather() else None,
                ATTR_CLOUDS: str(obs.sky_conditions()) if obs.sky_conditions() else None,
            }

            return data

        except (ClientError, Metar.ParserError) as err:
            _LOGGER.error("Error retrieving METAR data: %s", err)
            return None

class MetarSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a METAR sensor."""

    def __init__(self, coordinator: MetarDataUpdateCoordinator, station: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._station = station
        self._attr_name = f"{DEFAULT_NAME} {station}"
        self._attr_unique_id = f"{DOMAIN}_{station}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the device."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(ATTR_WEATHER)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}
            
        data = self.coordinator.data
        return {
            ATTR_ATTRIBUTION: "Data provided by NOAA",
            ATTR_STATION: data.get(ATTR_STATION),
            ATTR_LAST_UPDATE: data.get(ATTR_LAST_UPDATE),
            ATTR_TEMPERATURE: data.get(ATTR_TEMPERATURE),
            ATTR_DEWPOINT: data.get(ATTR_DEWPOINT),
            ATTR_WIND: data.get(ATTR_WIND),
            ATTR_VISIBILITY: data.get(ATTR_VISIBILITY),
            ATTR_PRESSURE: data.get(ATTR_PRESSURE),
            ATTR_CLOUDS: data.get(ATTR_CLOUDS),
        }

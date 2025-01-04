"""Constants for the METAR integration."""
from datetime import timedelta

from homeassistant.const import (
    TEMP_CELSIUS,
    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
)

DOMAIN = "metar"
PLATFORMS = ["sensor"]

CONF_STATION = "station"
DEFAULT_NAME = "METAR"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=30)

ATTR_STATION = "station"
ATTR_RAW = "raw"
ATTR_LAST_UPDATE = "last_update"

# sensor.py
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
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    TEMP_CELSIUS,
    LENGTH_KILOMETERS,
    PRESSURE_HPA,
    SPEED_KILOMETERS_PER_HOUR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    ATTR_RAW,
    ATTR_STATION,
    ATTR_LAST_UPDATE,
    CONF_STATION,
    DEFAULT_NAME,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

METAR_BASE_URL = "https://tgftp.nws.noaa.gov/data/observations/metar/stations"

SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="dewpoint",
        name="Dewpoint",
        native_unit_of_measurement=TEMP_CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_speed",
        name="Wind Speed",
        native_unit_of_measurement=SPEED_KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wind_direction",
        name="Wind Direction",
        icon="mdi:compass",
    ),
    SensorEntityDescription(
        key="visibility",
        name="Visibility",
        native_unit_of_measurement=LENGTH_KILOMETERS,
        icon="mdi:eye",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="pressure",
        name="Pressure",
        native_unit_of_measurement=PRESSURE_HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="weather",
        name="Weather",
        icon="mdi:weather-partly-cloudy",
    ),
    SensorEntityDescription(
        key="clouds",
        name="Clouds",
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key="raw",
        name="Raw METAR",
        icon="mdi:text",
    ),
)

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

    entities = []
    for description in SENSOR_TYPES:
        entities.append(MetarSensor(coordinator, station, description))

    async_add_entities(entities, True)

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
        self._raw_metar = None

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
            self._raw_metar = metar_data
            obs = Metar.Metar(metar_data)

            data = {
                "station": obs.station_id,
                "raw": metar_data,
                "last_update": obs.time,
                "temperature": obs.temp.value("C") if obs.temp else None,
                "dewpoint": obs.dewpt.value("C") if obs.dewpt else None,
                "wind_speed": obs.wind_speed.value("KMH") if obs.wind_speed else None,
                "wind_direction": obs.wind_dir.compass() if obs.wind_dir else None,
                "visibility": obs.vis.value("KM") if obs.vis else None,
                "pressure": obs.press.value("HPA") if obs.press else None,
                "weather": str(obs.present_weather()) if obs.present_weather() else None,
                "clouds": str(obs.sky_conditions()) if obs.sky_conditions() else None,
            }

            return data

        except (ClientError, Metar.ParserError) as err:
            _LOGGER.error("Error retrieving METAR data: %s", err)
            return None

class MetarSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a METAR sensor."""

    def __init__(
        self,
        coordinator: MetarDataUpdateCoordinator,
        station: str,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._station = station
        self._attr_name = f"{DEFAULT_NAME} {station} {description.name}"
        self._attr_unique_id = f"{DOMAIN}_{station}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the device."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if self.coordinator.data is None:
            return {}
            
        attrs = {
            ATTR_ATTRIBUTION: "Data provided by NOAA",
            ATTR_STATION: self.coordinator.data.get("station"),
            ATTR_LAST_UPDATE: self.coordinator.data.get("last_update"),
        }
        
        if self.entity_description.key == "raw":
            attrs[ATTR_RAW] = self.coordinator.data.get("raw")
            
        return attrs

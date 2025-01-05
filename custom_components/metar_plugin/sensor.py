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
    UnitOfTemperature,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
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
    ATTR_TEMPERATURE,
    ATTR_DEWPOINT,
    ATTR_WIND_SPEED,
    ATTR_WIND_DIRECTION,
    ATTR_VISIBILITY,
    ATTR_PRESSURE,
    ATTR_WEATHER,
    ATTR_CLOUDS,
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
        key=ATTR_TEMPERATURE,
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_DEWPOINT,
        name="Dewpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_WIND_SPEED,
        name="Wind Speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.WIND_SPEED,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_WIND_DIRECTION,
        name="Wind Direction",
        icon="mdi:compass",
    ),
    SensorEntityDescription(
        key=ATTR_VISIBILITY,
        name="Visibility",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        icon="mdi:eye",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PRESSURE,
        name="Pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_WEATHER,
        name="Weather",
        icon="mdi:weather-partly-cloudy",
    ),
    SensorEntityDescription(
        key=ATTR_CLOUDS,
        name="Clouds",
        icon="mdi:cloud",
    ),
    SensorEntityDescription(
        key=ATTR_RAW,
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
                ATTR_STATION: obs.station_id,
                ATTR_RAW: metar_data,
                ATTR_LAST_UPDATE: obs.time,
                ATTR_TEMPERATURE: obs.temp.value("C") if obs.temp else None,
                ATTR_DEWPOINT: obs.dewpt.value("C") if obs.dewpt else None,
                ATTR_WIND_SPEED: obs.wind_speed.value("KMH") if obs.wind_speed else None,
                ATTR_WIND_DIRECTION: obs.wind_dir.compass() if obs.wind_dir else None,
                ATTR_VISIBILITY: obs.vis.value("KM") if obs.vis else None,
                ATTR_PRESSURE: obs.press.value("HPA") if obs.press else None,
                ATTR_WEATHER: str(obs.present_weather()) if obs.present_weather() else None,
                ATTR_CLOUDS: str(obs.sky_conditions()) if obs.sky_conditions() else None,
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
            ATTR_STATION: self.coordinator.data.get(ATTR_STATION),
            ATTR_LAST_UPDATE: self.coordinator.data.get(ATTR_LAST_UPDATE),
        }
        
        if self.entity_description.key == ATTR_RAW:
            attrs[ATTR_RAW] = self.coordinator.data.get(ATTR_RAW)
            
        return attrs

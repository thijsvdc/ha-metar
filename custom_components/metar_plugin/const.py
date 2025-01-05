"""Constants for the METAR integration."""
from datetime import timedelta

from homeassistant.const import (
    UnitOfTemperature,
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
)

DOMAIN = "metar"
PLATFORMS = ["sensor"]

CONF_STATION = "station"
DEFAULT_NAME = "METAR"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=30)

# Attributes
ATTR_STATION = "station"
ATTR_RAW = "raw"
ATTR_LAST_UPDATE = "last_update"
ATTR_TEMPERATURE = "temperature"
ATTR_DEWPOINT = "dewpoint"
ATTR_WIND = "wind"
ATTR_WIND_SPEED = "wind_speed"
ATTR_WIND_DIRECTION = "wind_direction"
ATTR_VISIBILITY = "visibility"
ATTR_PRESSURE = "pressure"
ATTR_WEATHER = "weather"
ATTR_CLOUDS = "clouds"

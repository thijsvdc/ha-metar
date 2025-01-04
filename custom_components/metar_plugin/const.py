"""Constants for the METAR integration."""
from datetime import timedelta

DOMAIN = "metar"
PLATFORMS = ["sensor"]

CONF_STATION = "station"
DEFAULT_NAME = "METAR"
DEFAULT_UPDATE_INTERVAL = timedelta(minutes=30)

ATTR_STATION = "station"
ATTR_LAST_UPDATE = "last_update"
ATTR_TEMPERATURE = "temperature"
ATTR_DEWPOINT = "dewpoint"
ATTR_WIND = "wind"
ATTR_VISIBILITY = "visibility"
ATTR_PRESSURE = "pressure"
ATTR_WEATHER = "weather"
ATTR_CLOUDS = "clouds"

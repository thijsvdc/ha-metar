# METAR HACS Plugin

A Home Assistant plugin to display METAR data for selected ICAO airport codes.
During installation of the plugin, the user can select an ICAO code, which will pull the current METAR info from https://tgftp.nws.noaa.gov/data/observations/metar/stations/.
Raw metar, as well as all separate attributes can be retreived as entities.
After installation, multiple ICAO airport codes can be added.

## Installation

1. Copy the `custom_components/metar_plugin` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration from the Home Assistant Configuration panel.

## Configuration

1. Provide the ICAO code and update interval in the plugin settings.
2. Save and restart Home Assistant.

## License

This project is licensed under the terms of the Apache 2.O license.

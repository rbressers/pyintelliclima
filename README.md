# pyintelliclima

<div align="center">

[![Python versions](https://img.shields.io/pypi/pyversions/pyintelliclima)](https://www.python.org/downloads/)
[![PyPI](https://img.shields.io/pypi/v/pyintelliclima.svg)](https://pypi.org/project/pyintelliclima/)
[![Status](https://img.shields.io/pypi/status/pyintelliclima.svg)](https://pypi.org/project/pyintelliclima/)
[![License](https://img.shields.io/pypi/l/pyintelliclima)](https://github.com/dvdinth/pyintelliclima/blob/main/LICENSE)

</div>

* * *

This is a Python module for communicating with IntelliClima ECOCOMFORT 2.0 and
ECOCOMFORT 3 devices.
Its main use is for my corresponding [HomeAssistant IntelliClima integration](https://www.home-assistant.io/integrations/intelliclima/).

It can be extended to include other devices from IntelliClima in the future, but I only own the 
ECOCOMFORT 2.0, so I cannot add any others without help from device owners. I've made a
[guide for adding new devices](ADD_DEVICE_GUIDE.md). If you own another device type, it's
highly appreciated if you could take a look at the guide and see if you can add a PR for your
device(s), or share the logs as described so I can add them.

This API was made by reverse engineering the cloud API, through the use of an android emulator and proxy to catch the Intelliclima+ app traffic. As such, no public API exists and the functionality of this module breaks if the API changes. This module is provided as-is, with no guarantees of correctness, stability, or continued functionality. Use it at your own risk.

### ECOCOMFORT 3 air-quality values

ECOCOMFORT 3 reports separate VOC, CO2, and air-quality-index fields:

- `voc_state` is the same device-reported VOC channel exposed by ECOCOMFORT 2.
- `co2` is a separate manufacturer-designated CO2 channel. Field observations found physically
  implausible values and poor agreement with a reference CO2 monitor, so consumers should treat
  it as unverified raw data rather than a dependable ppm measurement.
- `aqi` is the device's five-level indoor air-quality index.

All three values are returned as strings. The distinction is also present in the official
Intelliclima+ app, which parses separate VOC, CO2, and AQI channels for ECOCOMFORT 3.

## Credits

This was highly inspired by: https://github.com/ruizmarc/homebridge-intelliclima

Partial credit for the reverse engineering process of the API goes to them.

* * *

## Project Docs

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*

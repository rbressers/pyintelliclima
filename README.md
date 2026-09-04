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

ECOCOMFORT 3 status responses populate the existing `voc_state`, `co2`, `aqi`, and `co2_thrs`
fields. All values are returned as strings. Their exact sensor semantics have not yet been
verified: field observations found physically implausible `co2` values, while `voc_state` has a
400-unit floor characteristic of a VOC-derived eCO2 estimate. Consumers should therefore expose
these fields as unverified raw data rather than dependable VOC or CO2 measurements.

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

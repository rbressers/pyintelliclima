from enum import StrEnum

# API endpoints
API_BASE_URL = "https://intelliclima.fantinicosmi.it"
API_MONO = "/server_v1_mono/api/"

REFRESH_DELAY = 5  # seconds


class FanSpeed(StrEnum):
    """Fan speed options for EcoComfort VMC devices."""

    off = "0"
    sleep = "1"
    low = "2"
    medium = "3"
    high = "4"
    auto_get = "16"  # The value when getting device status that indicates auto mode
    auto_set = "10"  # The value used when sending the command to set the device to auto mode


class FanMode(StrEnum):
    """Fan mode/direction options for EcoComfort VMC devices."""

    off = "0"
    inward = "1"
    outward = "2"
    alternate = "3"
    sensor = "4"


class Season(StrEnum):
    """Winter/summer mode for EcoComfort VMC devices."""

    winter = "0"
    summer = "1"


class FreeCoolingLevel(StrEnum):
    """Free cooling intake/outdoor delta threshold, only effective in summer mode."""

    off = "0"
    low = "1"
    medium = "2"
    high = "3"


class SlaveRotation(StrEnum):
    """Direction of rotation for a slave/satellite unit relative to its master."""

    concordant = "1"
    discordant = "2"


class ThresholdLevel(StrEnum):
    """Sensor-mode threshold levels for humidity/VOC/luminosity triggers."""

    off = "0"
    low = "1"
    medium = "2"
    high = "3"

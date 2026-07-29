from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyintelliclima.api import (
    IntelliClimaEcocomfortAPI,
    create_advanced_settings_command,
    create_offsets_command,
)
from pyintelliclima.const import FreeCoolingLevel, Season, SlaveRotation, ThresholdLevel

# --- create_offsets_command: golden values from real mitmproxy captures (2026-07-29) ---


@pytest.mark.parametrize(
    ("temperature_offset", "humidity_offset", "expected"),
    [
        (1.5, 0, "0A000005FE00102F00210000009600003D0D"),
        (-2.3, 0, "0A000005FE00102F00210000FF1A0000440D"),
        (0, 3, "0A000005FE00102F002100000000012CE60D"),
        (0, -5, "0A000005FE00102F002100000000FE0CE10D"),
        (0, 0, "0A000005FE00102F0021000000000000E90D"),
    ],
    ids=["temp_1.5", "temp_-2.3", "hum_3", "hum_-5", "zero"],
)
def test_create_offsets_command_matches_capture(temperature_offset, humidity_offset, expected):
    assert create_offsets_command("000005fe", temperature_offset, humidity_offset) == expected


# --- create_advanced_settings_command: golden values from real mitmproxy captures ---


def test_create_advanced_settings_command_rotation_concordant():
    command = create_advanced_settings_command("000005e8", slave_rotation=SlaveRotation.concordant)
    assert command == "0A000005E800182F002000007F7F7F7F7F01000000000000000D"


def test_create_advanced_settings_command_rotation_discordant():
    command = create_advanced_settings_command("000005e8", slave_rotation=SlaveRotation.discordant)
    assert command == "0A000005E800182F002000007F7F7F7F7F020000000000000A0D"


def test_create_advanced_settings_command_thresholds_combined():
    """All three thresholds share one register - all must be sent together."""
    command = create_advanced_settings_command(
        "000005fe",
        humidity_threshold=ThresholdLevel.high,
        humidity_threshold_advanced=True,
        lux_threshold=ThresholdLevel.low,
        voc_threshold=ThresholdLevel.low,
        voc_threshold_advanced=True,
    )
    assert command == "0A000005FE00182F002000007F8301817F7F0000000000008E0D"


def test_create_advanced_settings_command_defaults_all_preserved():
    """With no fields set, every settable byte is 0x7F (preserve)."""
    command = create_advanced_settings_command("000005fe")
    assert "7F7F7F7F7F" in command


def test_create_advanced_settings_command_threshold_off_ignores_advanced_flag():
    command = create_advanced_settings_command(
        "000005fe", humidity_threshold=ThresholdLevel.off, humidity_threshold_advanced=True
    )
    # byte after the leading "7F" preserve byte is the humidity threshold byte
    payload = command[16 : 16 + 2]
    assert payload == "00"


# --- async wrapper methods ---


@pytest.mark.asyncio
@patch("pyintelliclima.api.REFRESH_DELAY", 0)
@patch("pyintelliclima.api.post_to_session", new_callable=AsyncMock)
async def test_set_season(mock_post):
    session = MagicMock()
    api = IntelliClimaEcocomfortAPI(session, token_headers={"TOKEN": "tok"})
    mock_post.return_value = {"status": "OK", "serial": "000005fe"}

    result = await api.set_season("000005fe", Season.winter)

    assert result is True
    mock_post.assert_awaited_once()
    called_args, called_kwargs = mock_post.call_args
    assert called_args[1] == "eco/setdata/"
    assert called_kwargs["json_payload"] == {"serial": "000005fe", "data": '{"ws": 0}'}


@pytest.mark.asyncio
@patch("pyintelliclima.api.REFRESH_DELAY", 0)
@patch("pyintelliclima.api.post_to_session", new_callable=AsyncMock)
async def test_set_free_cooling(mock_post):
    session = MagicMock()
    api = IntelliClimaEcocomfortAPI(session, token_headers={"TOKEN": "tok"})
    mock_post.return_value = {"status": "OK", "value": 2, "serial": "000005fe"}

    result = await api.set_free_cooling("000005fe", FreeCoolingLevel.medium)

    assert result is True
    called_args, called_kwargs = mock_post.call_args
    assert called_args[1] == "eco/freecoolset/"
    assert called_kwargs["json_payload"] == {"serial": "000005fe", "value": 2}


@pytest.mark.asyncio
@patch("pyintelliclima.api.REFRESH_DELAY", 0)
@patch("pyintelliclima.api.post_to_session", new_callable=AsyncMock)
async def test_set_temperature_and_humidity_offsets(mock_post):
    session = MagicMock()
    api = IntelliClimaEcocomfortAPI(session, token_headers={"TOKEN": "tok"})
    mock_post.return_value = {"status": "OK"}

    result = await api.set_temperature_and_humidity_offsets("000005fe", 1.5, 0)

    assert result is True
    called_args, called_kwargs = mock_post.call_args
    assert called_args[1] == "eco/send/"
    assert called_kwargs["json_payload"] == {"trama": "0A000005FE00102F00210000009600003D0D"}


@pytest.mark.asyncio
@patch.object(IntelliClimaEcocomfortAPI, "set_advanced_settings", new_callable=AsyncMock)
async def test_set_slave_rotation_calls_set_advanced_settings(mock_set_advanced):
    session = MagicMock()
    api = IntelliClimaEcocomfortAPI(session, token_headers={})
    mock_set_advanced.return_value = True

    result = await api.set_slave_rotation("000005e8", SlaveRotation.concordant)

    assert result is True
    mock_set_advanced.assert_awaited_once_with("000005e8", slave_rotation=SlaveRotation.concordant)

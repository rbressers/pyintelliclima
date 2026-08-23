from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pyintelliclima.api import IntelliClimaAPI, IntelliClimaEcocomfort3API
from pyintelliclima.const import FanMode, FanSpeed

pytestmark = pytest.mark.asyncio


async def test_set_token_headers():
    api = IntelliClimaEcocomfort3API(MagicMock(), token_headers={"TOKEN": "old"})

    await api.set_token_headers({"TOKEN": "new"})

    assert api._token_headers == {"TOKEN": "new"}


@patch("pyintelliclima.api.REFRESH_DELAY", 0)
@patch("pyintelliclima.api.post_to_session", new_callable=AsyncMock)
async def test_set_mode_speed_uses_eco3_endpoint(mock_post):
    session = MagicMock()
    api = IntelliClimaEcocomfort3API(session, token_headers={"TOKEN": "tok"})
    mock_post.return_value = {"status": "OK"}

    result = await api.set_mode_speed("AABBCCDD", FanMode.alternate, FanSpeed.high)

    assert result is True
    mock_post.assert_awaited_once_with(
        session,
        "eco3/send/",
        headers={"TOKEN": "tok"},
        json_payload={"trama": "0AAABBCCDD000E2F005000000304620D"},
    )


@patch.object(IntelliClimaEcocomfort3API, "set_mode_speed", new_callable=AsyncMock)
async def test_turn_off(mock_set_mode_speed):
    api = IntelliClimaEcocomfort3API(MagicMock(), token_headers={})
    mock_set_mode_speed.return_value = True

    assert await api.turn_off("AABBCCDD") is True
    mock_set_mode_speed.assert_awaited_once_with("AABBCCDD", mode=FanMode.off, speed=FanSpeed.off)


@patch.object(IntelliClimaEcocomfort3API, "set_mode_speed", new_callable=AsyncMock)
async def test_set_mode_speed_auto(mock_set_mode_speed):
    api = IntelliClimaEcocomfort3API(MagicMock(), token_headers={})
    mock_set_mode_speed.return_value = True

    assert await api.set_mode_speed_auto("AABBCCDD") is True
    mock_set_mode_speed.assert_awaited_once_with(
        "AABBCCDD", mode=FanMode.sensor, speed=FanSpeed.auto_set
    )


async def test_main_api_updates_eco3_token_headers():
    api = IntelliClimaAPI(MagicMock(), username="user", password="pass")

    await api.set_all_token_headers({"TOKENID": "1", "TOKEN": "new"})

    assert api.ecocomfort3._token_headers == {"TOKENID": "1", "TOKEN": "new"}

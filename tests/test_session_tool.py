"""Tests for tools/session/session.py — written TDD-first."""

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.tools.session.session import SessionDataResponse, get_session_data


def _make_driver_info(drv: str) -> dict:
    return {
        "DriverNumber": "1" if drv == "VER" else "44" if drv == "HAM" else "16",
        "Abbreviation": drv,
        "BroadcastName": drv,
        "TeamName": "Red Bull" if drv == "VER" else "Mercedes" if drv == "HAM" else "Ferrari",
        "TeamColor": "3671C6",
        "FirstName": "Max" if drv == "VER" else "Lewis" if drv == "HAM" else "Charles",
        "LastName": "Verstappen" if drv == "VER" else "Hamilton" if drv == "HAM" else "Leclerc",
        "FullName": "Max Verstappen"
        if drv == "VER"
        else "Lewis Hamilton"
        if drv == "HAM"
        else "Charles Leclerc",
        "Status": "Finished",
        "Points": 25.0,
        "Position": 1.0,
    }


def _make_session(drivers=("VER", "HAM")):
    session = MagicMock()
    session.name = "Race"
    session.date = "2024-05-26"
    session.event = MagicMock()
    session.event.EventName = "Monaco Grand Prix"
    session.event.Location = "Monaco"
    session.event.Country = "Monaco"
    session.event.RoundNumber = 8
    session.total_laps = 78

    # laps mock
    laps = MagicMock()
    laps.__len__ = MagicMock(return_value=0)
    laps.pick_fastest.return_value = None
    session.laps = laps

    # weather_data mock
    weather = MagicMock()
    weather.__len__ = MagicMock(return_value=0)
    weather.empty = True
    session.weather_data = weather

    session.drivers = list(drivers)
    session.get_driver.side_effect = lambda drv: _make_driver_info(drv)
    return session


# ---------------------------------------------------------------------------
# top-level error propagation
# ---------------------------------------------------------------------------


@patch("pitstop.tools.session.session.fastf1_client")
def test_raises_tool_error_on_get_session_failure(mock_client):
    mock_client.get_session.side_effect = RuntimeError("network error")
    with pytest.raises(ToolError):
        get_session_data(2024, "Monaco", "R")


@patch("pitstop.tools.session.session.fastf1_client")
def test_raises_tool_error_on_load_failure(mock_client):
    session = _make_session()
    session.load.side_effect = RuntimeError("cache miss")
    mock_client.get_session.return_value = session
    with pytest.raises(ToolError):
        get_session_data(2024, "Monaco", "R")


# ---------------------------------------------------------------------------
# pagination
# ---------------------------------------------------------------------------


@patch("pitstop.tools.session.session.fastf1_client")
def test_results_pagination_page2(mock_client):
    session = _make_session(("VER", "HAM", "LEC"))
    mock_client.get_session.return_value = session

    result = get_session_data(2024, "Monaco", "R", includes=["results"], page=2, page_size=1)

    assert result.results is not None
    assert len(result.results.results) == 1
    assert result.results.results[0].abbreviation == "HAM"
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 3
    assert result.pagination.has_prev is True
    assert result.pagination.has_next is True


@patch("pitstop.tools.session.session.fastf1_client")
def test_drivers_pagination(mock_client):
    session = _make_session(("VER", "HAM", "LEC"))
    mock_client.get_session.return_value = session

    result = get_session_data(2024, "Monaco", "R", includes=["drivers"], page=1, page_size=2)

    assert result.drivers is not None
    assert len(result.drivers.drivers) == 2
    assert result.pagination is not None
    assert result.pagination.total_items == 3


# ---------------------------------------------------------------------------
# partial errors
# ---------------------------------------------------------------------------


@patch("pitstop.tools.session.session.fastf1_client")
def test_results_partial_error_on_driver_failure(mock_client):
    session = _make_session(("VER", "HAM"))

    def failing_get_driver(drv):
        if drv == "HAM":
            raise RuntimeError("driver data missing")
        return _make_driver_info(drv)

    session.get_driver.side_effect = failing_get_driver
    mock_client.get_session.return_value = session

    result = get_session_data(2024, "Monaco", "R", includes=["results"])

    assert result.results is not None
    assert len(result.results.results) == 1
    assert result.results.results[0].abbreviation == "VER"
    assert result.partial_errors is not None
    assert result.partial_errors.has_errors
    assert any("HAM" in e.item for e in result.partial_errors.errors)


@patch("pitstop.tools.session.session.fastf1_client")
def test_returns_session_data_response(mock_client):
    session = _make_session()
    mock_client.get_session.return_value = session

    result = get_session_data(2024, "Monaco", "R", includes=["results"])

    assert isinstance(result, SessionDataResponse)

"""Tests for tools/standings/standings.py — TDD-first."""

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.tools.standings.standings import get_standings


def _driver_row(family, given, team="Mercedes", position=1):
    return {
        "position": position,
        "positionText": str(position),
        "points": 100.0,
        "wins": 5,
        "driverId": family.lower(),
        "driverNumber": 44,
        "driverCode": family[:3].upper(),
        "givenName": given,
        "familyName": family,
        "dateOfBirth": "1985-01-07",
        "driverNationality": "British",
        "constructorIds": [team.lower().replace(" ", "_")],
        "constructorNames": [team],
        "constructorNationalities": ["German"],
    }


def _constructor_row(name, position=1):
    return {
        "position": position,
        "positionText": str(position),
        "points": 100.0,
        "wins": 5,
        "constructorId": name.lower().replace(" ", "_"),
        "constructorName": name,
        "constructorNationality": "British",
    }


@patch("pitstop.tools.standings.standings.fastf1_client")
def test_driver_name_filter(mock_client):
    rows = [
        _driver_row("Hamilton", "Lewis", position=1),
        _driver_row("Verstappen", "Max", team="Red Bull", position=2),
    ]
    mock_client.ergast.get_driver_standings.return_value.to_dict.return_value = rows
    result = get_standings(2024, type="driver", driver_name="Hamilton")
    assert result.drivers is not None
    assert len(result.drivers) == 1
    assert result.drivers[0].family_name == "Hamilton"


@patch("pitstop.tools.standings.standings.fastf1_client")
def test_team_name_filter_constructor(mock_client):
    rows = [
        _constructor_row("Red Bull", position=1),
        _constructor_row("Mercedes", position=2),
    ]
    mock_client.ergast.get_constructor_standings.return_value.to_dict.return_value = rows
    result = get_standings(2024, type="constructor", team_name="Red Bull")
    assert result.constructors is not None
    assert len(result.constructors) == 1
    assert result.constructors[0].constructor_name == "Red Bull"


@patch("pitstop.tools.standings.standings.fastf1_client")
def test_invalid_round_name_raises_tool_error(mock_client):
    schedule_mock = MagicMock()
    schedule_mock.to_dict.return_value = [
        {
            "RoundNumber": 1,
            "EventName": "Bahrain Grand Prix",
            "Country": "Bahrain",
            "Location": "Sakhir",
        }
    ]
    mock_client.get_event_schedule.return_value = schedule_mock
    with pytest.raises(ToolError):
        get_standings(2024, round="Nonexistent GP", type="driver")


@patch("pitstop.tools.standings.standings.fastf1_client")
def test_pagination(mock_client):
    rows = [
        _driver_row("Hamilton", "Lewis", position=1),
        _driver_row("Verstappen", "Max", team="Red Bull", position=2),
        _driver_row("Leclerc", "Charles", team="Ferrari", position=3),
    ]
    mock_client.ergast.get_driver_standings.return_value.to_dict.return_value = rows
    result = get_standings(2024, type="driver", page=2, page_size=1)
    assert result.drivers is not None
    assert len(result.drivers) == 1
    assert result.drivers[0].family_name == "Verstappen"
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 3
    assert result.pagination.has_prev is True

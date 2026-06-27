"""Tests for tools/schedule/schedule.py — TDD-first."""

from unittest.mock import MagicMock, patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.tools.schedule.schedule import get_schedule


def _event_row(name, country, location, round_num=1):
    return {
        "RoundNumber": round_num,
        "EventName": name,
        "Country": country,
        "Location": location,
        "OfficialEventName": f"Formula 1 {name}",
        "EventDate": "2024-05-26 00:00:00",
        "EventFormat": "conventional",
        "Session1Date": None,
        "Session2Date": None,
        "Session3Date": None,
        "Session4Date": None,
        "Session5Date": None,
        "Session1": "Practice 1",
        "Session2": "Practice 2",
        "Session3": "Practice 3",
        "Session4": "Qualifying",
        "Session5": "Race",
    }


def _make_df(rows):
    m = MagicMock()
    m.to_dict.return_value = rows
    return m


@patch("pitstop.tools.schedule.schedule.fastf1_client")
def test_event_name_filter(mock_client):
    rows = [
        _event_row("Monaco Grand Prix", "Monaco", "Monte Carlo", 8),
        _event_row("British Grand Prix", "United Kingdom", "Silverstone", 10),
    ]
    mock_client.get_event_schedule.return_value = _make_df(rows)
    result = get_schedule(2024, event_name="Monaco")
    assert len(result.events) == 1
    assert result.events[0].event_name == "Monaco Grand Prix"


@patch("pitstop.tools.schedule.schedule.fastf1_client")
def test_only_remaining_calls_get_events_remaining(mock_client):
    rows = [_event_row("Singapore Grand Prix", "Singapore", "Marina Bay", 18)]
    mock_client.get_events_remaining.return_value = _make_df(rows)
    result = get_schedule(2024, only_remaining=True)
    mock_client.get_events_remaining.assert_called_once()
    assert len(result.events) == 1
    assert result.events[0].event_name == "Singapore Grand Prix"


@patch("pitstop.tools.schedule.schedule.fastf1_client")
def test_pagination_correct_meta(mock_client):
    rows = [_event_row(f"GP {i}", "Country", "City", i) for i in range(1, 4)]
    mock_client.get_event_schedule.return_value = _make_df(rows)
    result = get_schedule(2024, include_testing=False, page=2, page_size=1)
    assert len(result.events) == 1
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 3
    assert result.pagination.has_prev is True
    assert result.pagination.has_next is True


@patch("pitstop.tools.schedule.schedule.fastf1_client")
def test_fastf1_failure_raises_tool_error(mock_client):
    mock_client.get_event_schedule.side_effect = RuntimeError("FastF1 down")
    with pytest.raises(ToolError):
        get_schedule(2024)

"""Tests for tools/live/live_data.py — TDD-first."""

from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.tools.live.live_data import get_live_data

SESSION = [{"session_key": 9999}]


def _interval(n: int) -> dict:
    return {
        "date": f"2024-05-26T14:0{n}:00",
        "driver_number": n,
        "gap_to_leader": n * 1.5,
        "interval": n * 0.5,
        "session_key": 9999,
        "meeting_key": 1234,
    }


def _stint(n: int) -> dict:
    return {
        "stint_number": n,
        "driver_number": n,
        "compound": "SOFT",
        "lap_start": n * 10,
        "lap_end": n * 10 + 9,
        "tyre_age_at_start": 0,
    }


def _weather(n: int) -> dict:
    return {
        "date": f"2024-05-26T14:0{n}:00",
        "air_temperature": 25.0 + n,
        "track_temperature": 35.0 + n,
        "humidity": 50.0,
        "pressure": 1013.0,
        "rainfall": 0.0,
        "wind_direction": 180.0,
        "wind_speed": 2.0,
        "session_key": 9999,
        "meeting_key": 1234,
    }


def _position(n: int) -> dict:
    return {
        "date": f"2024-05-26T14:0{n}:00",
        "driver_number": n,
        "position": n,
        "session_key": 9999,
        "meeting_key": 1234,
    }


def _lap(n: int) -> dict:
    return {
        "driver_number": n,
        "lap_number": n,
        "lap_duration": 90.0 + n,
        "duration_sector_1": 30.0,
        "duration_sector_2": 30.0,
        "duration_sector_3": 30.0,
        "i1_speed": 300.0,
        "i2_speed": 290.0,
        "st_speed": 320.0,
        "is_pit_out_lap": False,
        "date_start": f"2024-05-26T14:0{n}:00",
        "session_key": 9999,
        "meeting_key": 1234,
    }


def _overtake(n: int) -> dict:
    return {
        "date": f"2024-05-26T14:0{n}:00",
        "overtaking_driver_number": n,
        "overtaken_driver_number": n + 1,
        "position": n,
        "session_key": 9999,
        "meeting_key": 1234,
    }


@patch("pitstop.clients.openf1_client.query")
def test_intervals_calls_query_with_correct_endpoint(mock_query):
    def side(ep, **kw):
        return SESSION if ep == "/sessions" else [_interval(1)]

    mock_query.side_effect = side
    result = get_live_data(["intervals"], 2024, "Monaco")
    assert result.intervals is not None
    endpoints = [c.args[0] for c in mock_query.call_args_list]
    assert "/intervals" in endpoints


@patch("pitstop.clients.openf1_client.query")
def test_two_data_types_calls_both_endpoints(mock_query):
    def side(ep, **kw):
        if ep == "/sessions":
            return SESSION
        if ep == "/intervals":
            return [_interval(1)]
        if ep == "/stints":
            return [_stint(1)]
        return []

    mock_query.side_effect = side
    result = get_live_data(["intervals", "stints"], 2024, "Monaco")
    endpoints = [c.args[0] for c in mock_query.call_args_list]
    assert "/intervals" in endpoints
    assert "/stints" in endpoints
    assert result.intervals is not None
    assert result.stints is not None


@patch("pitstop.clients.openf1_client.query")
def test_unknown_data_type_is_skipped(mock_query):
    mock_query.return_value = SESSION
    result = get_live_data(["bogus"], 2024, "Monaco")
    assert result.intervals is None
    assert result.pit_stops is None
    assert result.partial_errors is None


@patch("pitstop.clients.openf1_client.query")
def test_pagination_returns_page_slice(mock_query):
    five_intervals = [_interval(i) for i in range(5)]

    def side(ep, **kw):
        return SESSION if ep == "/sessions" else five_intervals

    mock_query.side_effect = side
    result = get_live_data(["intervals"], 2024, "Monaco", page=1, page_size=2)
    assert result.intervals is not None
    assert len(result.intervals.intervals) == 2
    assert result.intervals.total_data_points == 5


@patch("pitstop.clients.openf1_client.query")
def test_partial_error_on_one_type_continues_others(mock_query):
    from pitstop.exceptions import DataSourceError

    def side(ep, **kw):
        if ep == "/sessions":
            return SESSION
        if ep == "/intervals":
            raise DataSourceError("openf1", ep, "timeout")
        if ep == "/stints":
            return [_stint(1)]
        return []

    mock_query.side_effect = side
    result = get_live_data(["intervals", "stints"], 2024, "Monaco")
    assert result.intervals is None
    assert result.stints is not None
    assert result.partial_errors is not None
    assert result.partial_errors.has_errors
    assert any("intervals" in e.item for e in result.partial_errors.errors)


@patch("pitstop.clients.openf1_client.query")
def test_session_failure_raises_tool_error(mock_query):
    from pitstop.exceptions import DataSourceError

    mock_query.side_effect = DataSourceError("openf1", "/sessions", "down")
    with pytest.raises(ToolError):
        get_live_data(["intervals"], 2024, "Monaco")


@patch("pitstop.clients.openf1_client.query")
def test_empty_session_returns_empty_response(mock_query):
    mock_query.return_value = []
    result = get_live_data(["intervals"], 2024, "Monaco")
    assert result.intervals is None
    assert result.year == 2024
    assert result.country == "Monaco"


@patch("pitstop.clients.openf1_client.query")
def test_new_data_types_populate_their_sections(mock_query):
    fixtures = {
        "/weather": _weather(1),
        "/position": _position(1),
        "/laps": _lap(1),
        "/overtakes": _overtake(1),
    }

    def side(ep, **kw):
        return SESSION if ep == "/sessions" else [fixtures[ep]]

    mock_query.side_effect = side
    result = get_live_data(["weather", "position", "laps", "overtakes"], 2024, "Monaco")
    assert result.weather is not None
    assert result.position is not None
    assert result.laps is not None
    assert result.overtakes is not None
    endpoints = {c.args[0] for c in mock_query.call_args_list}
    assert endpoints >= set(fixtures)


@patch("pitstop.clients.openf1_client.query")
def test_weather_omits_driver_number_filter(mock_query):
    def side(ep, **kw):
        return SESSION if ep == "/sessions" else [_weather(1)]

    mock_query.side_effect = side
    get_live_data(["weather"], 2024, "Monaco", driver_number=44)
    weather_call = next(c for c in mock_query.call_args_list if c.args[0] == "/weather")
    assert "driver_number" not in weather_call.kwargs


@patch("pitstop.clients.openf1_client.query")
def test_overtakes_maps_driver_number_to_overtaking_driver_number(mock_query):
    def side(ep, **kw):
        return SESSION if ep == "/sessions" else [_overtake(1)]

    mock_query.side_effect = side
    get_live_data(["overtakes"], 2024, "Monaco", driver_number=44)
    overtakes_call = next(c for c in mock_query.call_args_list if c.args[0] == "/overtakes")
    assert overtakes_call.kwargs.get("overtaking_driver_number") == 44
    assert "driver_number" not in overtakes_call.kwargs

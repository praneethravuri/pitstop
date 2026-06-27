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

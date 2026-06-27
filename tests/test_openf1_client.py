"""Tests for src/pitstop/clients/openf1_client.py (TDD — written before implementation)."""

import pytest

import pitstop.clients as clients_mod
from pitstop.clients.openf1_client import (
    get_car_data,
    get_intervals,
    get_location,
    get_meetings,
    get_pit_stops,
    get_race_control,
    get_sessions,
    get_stints,
    get_team_radio,
    query,
)
from pitstop.exceptions import DataSourceError


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the OpenF1 client singleton before and after each test."""
    clients_mod._openf1_client = None
    yield
    clients_mod._openf1_client = None


# ---------------------------------------------------------------------------
# query() — core function
# ---------------------------------------------------------------------------


def test_query_returns_list(httpx_mock):
    httpx_mock.add_response(json=[{"interval": 0.5}])
    result = query("/intervals", session_key=123)
    assert result == [{"interval": 0.5}]


def test_query_makes_get_to_correct_url(httpx_mock):
    httpx_mock.add_response(json=[])
    query("/intervals", session_key=123)
    req = httpx_mock.get_requests()[0]
    assert str(req.url) == "https://api.openf1.org/v1/intervals?session_key=123"


def test_query_drops_none_params(httpx_mock):
    httpx_mock.add_response(json=[])
    query("/intervals", session_key=None, driver_number=44)
    req = httpx_mock.get_requests()[0]
    # session_key=None must be stripped; driver_number=44 must remain
    assert "session_key" not in str(req.url)
    assert "driver_number=44" in str(req.url)


def test_query_all_none_params_gives_no_query_string(httpx_mock):
    httpx_mock.add_response(json=[])
    query("/intervals", session_key=None)
    req = httpx_mock.get_requests()[0]
    assert "?" not in str(req.url)


def test_query_raises_data_source_error_on_4xx(httpx_mock):
    httpx_mock.add_response(status_code=404)
    with pytest.raises(DataSourceError) as exc_info:
        query("/intervals")
    assert "openf1" in str(exc_info.value)


def test_query_raises_data_source_error_on_5xx(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with pytest.raises(DataSourceError) as exc_info:
        query("/sessions")
    assert "openf1" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Thin wrapper functions — one test each to confirm they call query()
# ---------------------------------------------------------------------------


def test_get_intervals_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"interval": 1.0}])
    result = get_intervals(session_key=123)
    assert result == [{"interval": 1.0}]
    req = httpx_mock.get_requests()[0]
    assert "/intervals" in str(req.url)
    assert "session_key=123" in str(req.url)


def test_get_pit_stops_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"pit_duration": 2.3}])
    result = get_pit_stops(session_key=9999)
    assert result == [{"pit_duration": 2.3}]
    req = httpx_mock.get_requests()[0]
    assert "/pit" in str(req.url)


def test_get_team_radio_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"recording_url": "http://example.com/radio.mp3"}])
    result = get_team_radio(driver_number=44)
    assert len(result) == 1
    req = httpx_mock.get_requests()[0]
    assert "/team_radio" in str(req.url)


def test_get_stints_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"compound": "SOFT"}])
    result = get_stints(session_key=1)
    assert result == [{"compound": "SOFT"}]
    req = httpx_mock.get_requests()[0]
    assert "/stints" in str(req.url)


def test_get_race_control_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"flag": "YELLOW"}])
    result = get_race_control(flag="YELLOW")
    assert result == [{"flag": "YELLOW"}]
    req = httpx_mock.get_requests()[0]
    assert "/race_control" in str(req.url)


def test_get_sessions_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"session_name": "Race"}])
    result = get_sessions(year=2024)
    assert result == [{"session_name": "Race"}]
    req = httpx_mock.get_requests()[0]
    assert "/sessions" in str(req.url)


def test_get_meetings_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"country_name": "Monaco"}])
    result = get_meetings(year=2024)
    assert result == [{"country_name": "Monaco"}]
    req = httpx_mock.get_requests()[0]
    assert "/meetings" in str(req.url)


def test_get_location_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"x": 100, "y": 200}])
    result = get_location(driver_number=1)
    assert result == [{"x": 100, "y": 200}]
    req = httpx_mock.get_requests()[0]
    assert "/location" in str(req.url)


def test_get_car_data_is_wrapper(httpx_mock):
    httpx_mock.add_response(json=[{"speed": 300}])
    result = get_car_data(session_key=42)
    assert result == [{"speed": 300}]
    req = httpx_mock.get_requests()[0]
    assert "/car_data" in str(req.url)

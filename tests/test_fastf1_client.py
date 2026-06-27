"""Tests for src/pitstop/clients/fastf1_client.py — TDD."""

import logging
from unittest.mock import patch

import pytest

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.exceptions import DataSourceError


def _client() -> FastF1Client:
    """Return a client with cache disabled so no disk I/O."""
    return FastF1Client(enable_cache=False)


# ---------------------------------------------------------------------------
# Logger identity
# ---------------------------------------------------------------------------


def test_logger_name():
    import pitstop.clients.fastf1_client as mod

    assert mod.logger.name == "pitstop.fastf1"


# ---------------------------------------------------------------------------
# get_session
# ---------------------------------------------------------------------------


def test_get_session_wraps_exception_as_data_source_error():
    client = _client()
    with patch("fastf1.get_session", side_effect=ValueError("no such session")):
        with pytest.raises(DataSourceError):
            client.get_session(2024, "Monza", "Q")


def test_get_session_data_source_error_attributes():
    client = _client()
    with patch("fastf1.get_session", side_effect=ValueError("boom")):
        with pytest.raises(DataSourceError) as exc_info:
            client.get_session(2024, "Monza", "Q")
        assert exc_info.value.source == "fastf1"
        assert exc_info.value.operation == "get_session"
        assert "boom" in exc_info.value.reason


def test_get_session_error_message_contains_operation():
    client = _client()
    with patch("fastf1.get_session", side_effect=ValueError("boom")):
        with pytest.raises(DataSourceError, match="get_session"):
            client.get_session(2024, "Monza", "Q")


def test_get_session_logs_debug_on_entry(caplog):
    client = _client()
    fake_session = object()
    with patch("fastf1.get_session", return_value=fake_session):
        with caplog.at_level(logging.DEBUG, logger="pitstop.fastf1"):
            result = client.get_session(2024, "Monza", "Q")
    assert result is fake_session
    assert any("get_session" in r.message for r in caplog.records)


def test_get_session_logs_error_on_failure(caplog):
    client = _client()
    with patch("fastf1.get_session", side_effect=RuntimeError("fail")):
        with caplog.at_level(logging.ERROR, logger="pitstop.fastf1"):
            with pytest.raises(DataSourceError):
                client.get_session(2024, "Monza", "Q")
    assert any(r.levelno == logging.ERROR for r in caplog.records)


# ---------------------------------------------------------------------------
# get_event_schedule
# ---------------------------------------------------------------------------


def test_get_event_schedule_wraps_exception():
    client = _client()
    with patch("fastf1.get_event_schedule", side_effect=ConnectionError("timeout")):
        with pytest.raises(DataSourceError, match="get_event_schedule"):
            client.get_event_schedule(2024)


def test_get_event_schedule_error_has_correct_source():
    client = _client()
    with patch("fastf1.get_event_schedule", side_effect=ConnectionError("timeout")):
        with pytest.raises(DataSourceError) as exc_info:
            client.get_event_schedule(2024)
        assert exc_info.value.source == "fastf1"


# ---------------------------------------------------------------------------
# get_event
# ---------------------------------------------------------------------------


def test_get_event_wraps_exception():
    client = _client()
    with patch("fastf1.get_event", side_effect=KeyError("Monza")):
        with pytest.raises(DataSourceError, match="Monza"):
            client.get_event(2024, "Monza")


def test_get_event_error_has_correct_operation():
    client = _client()
    with patch("fastf1.get_event", side_effect=KeyError("Monza")):
        with pytest.raises(DataSourceError) as exc_info:
            client.get_event(2024, "Monza")
        assert exc_info.value.operation == "get_event"


# ---------------------------------------------------------------------------
# get_testing_session
# ---------------------------------------------------------------------------


def test_get_testing_session_wraps_exception():
    client = _client()
    with patch("fastf1.get_testing_session", side_effect=ValueError("nope")):
        with pytest.raises(DataSourceError, match="get_testing_session"):
            client.get_testing_session(2024, 1, 2)


def test_get_testing_session_error_has_correct_source():
    client = _client()
    with patch("fastf1.get_testing_session", side_effect=ValueError("nope")):
        with pytest.raises(DataSourceError) as exc_info:
            client.get_testing_session(2024, 1, 2)
        assert exc_info.value.source == "fastf1"


# ---------------------------------------------------------------------------
# get_testing_event
# ---------------------------------------------------------------------------


def test_get_testing_event_wraps_exception():
    client = _client()
    with patch("fastf1.get_testing_event", side_effect=RuntimeError("fail")):
        with pytest.raises(DataSourceError, match="get_testing_event"):
            client.get_testing_event(2024, 1)


# ---------------------------------------------------------------------------
# get_events_remaining
# ---------------------------------------------------------------------------


def test_get_events_remaining_wraps_exception():
    client = _client()
    with patch("fastf1.get_events_remaining", side_effect=OSError("network")):
        with pytest.raises(DataSourceError, match="network"):
            client.get_events_remaining()

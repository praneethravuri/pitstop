"""Tests for tools/telemetry/telemetry.py — written TDD-first."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastmcp.exceptions import ToolError

from pitstop.tools.telemetry.telemetry import TelemetryDataResponse, get_telemetry_data


def _make_lap(driver: str, lap_num: int = 1, tel_df=None):
    lap = MagicMock()
    lap.__getitem__ = lambda self, k: {
        "Driver": driver,
        "LapTime": "1:12.000",
        "LapNumber": lap_num,
    }[k]
    if tel_df is None:
        # Empty telemetry to keep tests fast
        tel_df = MagicMock()
        tel_df.iterrows.return_value = iter([])
    lap.get_telemetry.return_value = tel_df
    return lap


def _make_telemetry_df(n_rows: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "SessionTime": [float(i) for i in range(n_rows)],
            "RPM": [10000] * n_rows,
            "Speed": [200.0] * n_rows,
            "Throttle": [100.0] * n_rows,
            "Brake": [0.0] * n_rows,
            "nGear": [7] * n_rows,
            "DRS": [1] * n_rows,
            "Distance": [float(i) * 10 for i in range(n_rows)],
            "X": [0.0] * n_rows,
            "Y": [0.0] * n_rows,
            "Z": [0.0] * n_rows,
        }
    )


def _make_driver_laps(driver: str, failing: bool = False, tel_df=None):
    driver_laps = MagicMock()
    driver_laps.__len__ = MagicMock(return_value=1)
    if failing:
        driver_laps.pick_fastest.side_effect = RuntimeError("telemetry unavailable")
    else:
        driver_laps.pick_fastest.return_value = _make_lap(driver, tel_df=tel_df)
    return driver_laps


def _make_session(drivers=("VER", "HAM"), failing_drivers=(), tel_df=None):
    session = MagicMock()
    session.name = "Qualifying"
    session.event = MagicMock()
    session.event.EventName = "Monaco Grand Prix"

    def pick_driver(drv):
        return _make_driver_laps(drv, failing=drv in failing_drivers, tel_df=tel_df)

    session.laps.pick_driver.side_effect = pick_driver
    return session


# ---------------------------------------------------------------------------
# top-level error propagation
# ---------------------------------------------------------------------------


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_raises_tool_error_on_get_session_failure(mock_client):
    mock_client.get_session.side_effect = RuntimeError("connection error")
    with pytest.raises(ToolError):
        get_telemetry_data(2024, "Monaco", "Q", ["VER"])


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_raises_tool_error_on_load_failure(mock_client):
    session = _make_session()
    session.load.side_effect = RuntimeError("cache miss")
    mock_client.get_session.return_value = session
    with pytest.raises(ToolError):
        get_telemetry_data(2024, "Monaco", "Q", ["VER"])


# ---------------------------------------------------------------------------
# partial errors
# ---------------------------------------------------------------------------


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_partial_error_when_one_driver_fails(mock_client):
    session = _make_session(("VER", "HAM"), failing_drivers=("HAM",))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER", "HAM"])

    assert len(result.drivers_telemetry) == 1
    assert result.drivers_telemetry[0].driver == "VER"
    assert result.partial_errors is not None
    assert result.partial_errors.has_errors
    assert any("HAM" in e.item for e in result.partial_errors.errors)


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_successful_drivers_returned_despite_partial_failure(mock_client):
    session = _make_session(("VER", "HAM", "LEC"), failing_drivers=("HAM",))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER", "HAM", "LEC"])

    drivers_returned = {t.driver for t in result.drivers_telemetry}
    assert drivers_returned == {"VER", "LEC"}
    assert result.partial_errors is not None
    assert len(result.partial_errors.errors) == 1


# ---------------------------------------------------------------------------
# pagination
# ---------------------------------------------------------------------------


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_telemetry_pagination_page2(mock_client):
    session = _make_session(("VER", "HAM", "LEC"))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER", "HAM", "LEC"], page=2, page_size=1)

    assert len(result.drivers_telemetry) == 1
    assert result.drivers_telemetry[0].driver == "HAM"
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 3
    assert result.pagination.has_prev is True
    assert result.pagination.has_next is True


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_telemetry_returns_response_type(mock_client):
    session = _make_session(("VER",))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER"])

    assert isinstance(result, TelemetryDataResponse)
    assert result.pagination is not None


# ---------------------------------------------------------------------------
# comparison
# ---------------------------------------------------------------------------


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_two_drivers_returns_comparison(mock_client):
    session = _make_session(("VER", "HAM"))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER", "HAM"])

    assert result.comparison is not None
    assert result.comparison.driver1 == "VER"
    assert result.comparison.driver2 == "HAM"
    assert result.comparison.session_name == "Qualifying"
    assert result.comparison.event_name == "Monaco Grand Prix"


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_one_driver_no_comparison(mock_client):
    session = _make_session(("VER",))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER"])

    assert result.comparison is None


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_three_drivers_no_comparison(mock_client):
    session = _make_session(("VER", "HAM", "LEC"))
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER", "HAM", "LEC"])

    assert result.comparison is None


# ---------------------------------------------------------------------------
# downsampling
# ---------------------------------------------------------------------------


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_downsampling_caps_points_at_max_points(mock_client):
    tel_df = _make_telemetry_df(500)
    session = _make_session(("VER",), tel_df=tel_df)
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER"])

    assert result.drivers_telemetry[0].total_points <= 100


@patch("pitstop.tools.telemetry.telemetry.fastf1_client")
def test_max_points_zero_disables_downsampling(mock_client):
    tel_df = _make_telemetry_df(500)
    session = _make_session(("VER",), tel_df=tel_df)
    mock_client.get_session.return_value = session

    result = get_telemetry_data(2024, "Monaco", "Q", ["VER"], max_points=0)

    assert result.drivers_telemetry[0].total_points == 500

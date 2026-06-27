"""Tests for tools/analysis/analysis.py."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastmcp.exceptions import ToolError

from pitstop.exceptions import DataSourceError
from pitstop.tools.analysis.analysis import get_race_analysis
from pitstop.tools.analysis.models import AnalysisResponse


def _make_laps(driver, n=5, compound="MEDIUM"):
    return pd.DataFrame(
        {
            "Driver": [driver] * n,
            "LapTime": pd.to_timedelta([f"0:1:3{i}.0" for i in range(n)]),
            "LapNumber": list(range(1, n + 1)),
            "Compound": [compound] * n,
            "Stint": [1] * n,
            "IsPersonalBest": [False] * n,
        }
    )


def _make_session(drivers=("VER",)):
    session = MagicMock()
    session.laps.pick_driver.side_effect = lambda d: _make_laps(d)
    return session


# ---------------------------------------------------------------------------
# pace
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_pace_analysis(mock_client):
    session = _make_session()
    mock_client.get_session.return_value = session

    result = get_race_analysis(2024, "Monaco", "R", ["VER", "HAM"], analysis_type="pace")

    assert isinstance(result, AnalysisResponse)
    assert result.pace is not None
    assert len(result.pace) == 2
    assert all(p.mean_lap_time_s is not None and p.mean_lap_time_s > 0 for p in result.pace)


# ---------------------------------------------------------------------------
# tire_degradation
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_tire_degradation(mock_client):
    session = _make_session()
    mock_client.get_session.return_value = session

    result = get_race_analysis(2024, "Monaco", "R", ["VER"], analysis_type="tire_degradation")

    assert result.tire_degradation is not None
    assert len(result.tire_degradation) >= 1
    entry = result.tire_degradation[0]
    assert entry.driver == "VER"
    assert entry.laps_on_compound == 5
    assert entry.degradation_rate_s_per_lap is not None  # 5 laps >= 3


# ---------------------------------------------------------------------------
# stints
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_stints_analysis(mock_client):
    session = _make_session()
    mock_client.get_session.return_value = session

    result = get_race_analysis(2024, "Monaco", "R", ["VER"], analysis_type="stints")

    assert result.stints is not None
    assert len(result.stints) >= 1
    stint = result.stints[0]
    assert stint.laps == 5
    assert stint.avg_lap_time_s is not None and stint.avg_lap_time_s > 0


# ---------------------------------------------------------------------------
# consistency
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_consistency_analysis(mock_client):
    session = _make_session()
    mock_client.get_session.return_value = session

    result = get_race_analysis(2024, "Monaco", "R", ["VER", "HAM"], analysis_type="consistency")

    assert result.consistency is not None
    assert len(result.consistency) == 2
    assert all(c.stddev_s is not None for c in result.consistency)
    assert all(c.consistency_rank is not None for c in result.consistency)


# ---------------------------------------------------------------------------
# partial errors
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_driver_load_failure_in_partial_errors(mock_client):
    session = MagicMock()

    def pick_driver(d):
        if d == "ERR":
            raise RuntimeError("telemetry unavailable")
        return _make_laps(d)

    session.laps.pick_driver.side_effect = pick_driver
    mock_client.get_session.return_value = session

    result = get_race_analysis(2024, "Monaco", "R", ["VER", "ERR"], analysis_type="pace")

    assert result.pace is not None
    assert len(result.pace) == 1
    assert result.pace[0].driver == "VER"
    assert result.partial_errors is not None
    assert result.partial_errors.has_errors
    assert any("ERR" in e.item for e in result.partial_errors.errors)


# ---------------------------------------------------------------------------
# session load failure
# ---------------------------------------------------------------------------


@patch("pitstop.tools.analysis.analysis.fastf1_client")
def test_session_load_failure_raises_tool_error(mock_client):
    mock_client.get_session.side_effect = DataSourceError("fastf1", "get_session", "not found")

    with pytest.raises(ToolError):
        get_race_analysis(2024, "Monaco", "R", ["VER"])

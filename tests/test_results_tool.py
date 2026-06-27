"""Tests for tools/results/results.py — TDD-first."""

from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.exceptions import DataSourceError
from pitstop.tools.results.results import get_results


def _race_response(n=2):
    results = [
        {
            "position": str(i),
            "Driver": {
                "driverId": f"driver{i}",
                "givenName": "First",
                "familyName": f"Last{i}",
            },
            "Constructor": {"name": "TestTeam"},
            "laps": "57",
            "Time": {"time": "1:30:00.000"},
            "status": "Finished",
            "points": str(25 - i),
            "grid": str(i),
        }
        for i in range(1, n + 1)
    ]
    return {
        "MRData": {
            "total": str(n),
            "RaceTable": {"Races": [{"raceName": "Bahrain Grand Prix", "Results": results}]},
        }
    }


def _qualifying_response():
    return {
        "MRData": {
            "total": "1",
            "RaceTable": {
                "Races": [
                    {
                        "raceName": "Bahrain Grand Prix",
                        "QualifyingResults": [
                            {
                                "position": "1",
                                "Driver": {
                                    "driverId": "verstappen",
                                    "givenName": "Max",
                                    "familyName": "Verstappen",
                                },
                                "Constructor": {"name": "Red Bull"},
                                "Q1": "1:29.000",
                                "Q2": "1:28.000",
                                "Q3": "1:26.720",
                            }
                        ],
                    }
                ]
            },
        }
    }


def _pitstop_response():
    return {
        "MRData": {
            "total": "1",
            "RaceTable": {
                "Races": [
                    {
                        "raceName": "Bahrain Grand Prix",
                        "PitStops": [
                            {
                                "driverId": "hamilton",
                                "stop": "1",
                                "lap": "20",
                                "time": "14:23:45",
                                "duration": "23.456",
                            }
                        ],
                    }
                ]
            },
        }
    }


def _status_response():
    return {
        "MRData": {
            "total": "2",
            "StatusTable": {
                "Status": [
                    {"statusId": "1", "count": "18", "status": "Finished"},
                    {"statusId": "11", "count": "2", "status": "Accident"},
                ]
            },
        }
    }


@patch("pitstop.tools.results.results.jolpica_client")
def test_race_results_returns_paginated_response(mock_jc):
    mock_jc.query.return_value = _race_response(n=2)
    result = get_results(2023, 1, result_type="race", page=1, page_size=10)
    assert result.race_results is not None
    assert len(result.race_results) == 2
    assert result.race_results[0].driver_id == "driver1"
    assert result.race_results[0].driver_name == "First Last1"
    assert result.race_results[0].position == 1
    assert result.race_results[0].points == 24.0
    assert result.race_name == "Bahrain Grand Prix"
    assert result.pagination is not None
    assert result.pagination.total_items == 2
    assert result.total_records == 2


@patch("pitstop.tools.results.results.jolpica_client")
def test_qualifying_results(mock_jc):
    mock_jc.query.return_value = _qualifying_response()
    result = get_results(2023, 1, result_type="qualifying")
    assert result.qualifying_results is not None
    assert len(result.qualifying_results) == 1
    qr = result.qualifying_results[0]
    assert qr.driver_id == "verstappen"
    assert qr.q3 == "1:26.720"
    assert qr.position == 1


@patch("pitstop.tools.results.results.jolpica_client")
def test_pitstops(mock_jc):
    mock_jc.query.return_value = _pitstop_response()
    result = get_results(2023, 1, result_type="pitstops")
    assert result.pit_stops is not None
    assert len(result.pit_stops) == 1
    ps = result.pit_stops[0]
    assert ps.driver_id == "hamilton"
    assert ps.lap == 20
    assert ps.duration == "23.456"


@patch("pitstop.tools.results.results.jolpica_client")
def test_status(mock_jc):
    mock_jc.query.return_value = _status_response()
    result = get_results(2023, 1, result_type="status")
    assert result.statuses is not None
    assert len(result.statuses) == 2
    assert result.statuses[0].status == "Finished"
    assert result.statuses[0].count == 18


@patch("pitstop.tools.results.results.jolpica_client")
def test_data_source_error_raises_tool_error(mock_jc):
    mock_jc.query.side_effect = DataSourceError("jolpica", "query", "timeout")
    with pytest.raises(ToolError):
        get_results(2023, 1, result_type="race")


@patch("pitstop.tools.results.results.jolpica_client")
def test_driver_filter_uses_path_segment(mock_jc):
    mock_jc.query.return_value = _race_response(n=1)
    get_results(2023, 1, result_type="race", driver="hamilton")
    mock_jc.query.assert_called_with("2023/1/drivers/hamilton/results", limit=30, offset=0)


@patch("pitstop.tools.results.results.jolpica_client")
def test_driver_filter_status_raises_tool_error(mock_jc):
    with pytest.raises(ToolError, match="not supported"):
        get_results(2023, 1, result_type="status", driver="hamilton")

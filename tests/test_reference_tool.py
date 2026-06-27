"""Tests for tools/reference/reference.py — TDD-first."""

import logging
from unittest.mock import patch

from pitstop.tools.reference.reference import get_reference_data


def _driver_row(given, family, driver_id=None, code=None):
    return {
        "driverId": driver_id or family.lower(),
        "driverNumber": 44,
        "driverCode": code or family[:3].upper(),
        "givenName": given,
        "familyName": family,
        "dateOfBirth": "1985-01-07",
        "nationality": "British",
    }


def _circuit_row(circuit_id, name, location, country):
    return {
        "circuitId": circuit_id,
        "circuitName": name,
        "location": location,
        "country": country,
        "lat": 43.7347,
        "lng": 7.4205,
        "url": f"https://en.wikipedia.org/wiki/{name.replace(' ', '_')}",
    }


@patch("pitstop.tools.reference.reference.fastf1_client")
def test_driver_name_filter(mock_client):
    rows = [_driver_row("Lewis", "Hamilton"), _driver_row("Max", "Verstappen")]
    mock_client.ergast.get_driver_info.return_value.to_dict.return_value = rows

    result = get_reference_data("driver", year=2024, name="Hamilton")

    assert result.drivers is not None
    assert len(result.drivers) == 1
    assert result.drivers[0].family_name == "Hamilton"
    assert result.name_filter == "Hamilton"


@patch("pitstop.tools.reference.reference.fastf1_client")
def test_driver_pagination(mock_client):
    rows = [
        _driver_row("Lewis", "Hamilton"),
        _driver_row("Max", "Verstappen"),
        _driver_row("Charles", "Leclerc"),
    ]
    mock_client.ergast.get_driver_info.return_value.to_dict.return_value = rows

    result = get_reference_data("driver", year=2024, page=2, page_size=2)

    assert result.drivers is not None
    assert len(result.drivers) == 1
    assert result.drivers[0].family_name == "Leclerc"
    assert result.pagination is not None
    assert result.pagination.page == 2
    assert result.pagination.total_items == 3
    assert result.pagination.has_prev is True
    assert result.pagination.has_next is False


@patch("pitstop.tools.reference.reference.fastf1_client")
def test_circuit_enrichment_failure_logs_warning(mock_client, caplog):
    rows = [_circuit_row("monaco", "Circuit de Monaco", "Monte-Carlo", "Monaco")]
    mock_client.ergast.get_circuits.return_value.to_dict.return_value = rows
    # Session lookup raises, triggering the enrichment failure path
    mock_client.get_session.side_effect = RuntimeError("session not found")

    with caplog.at_level(logging.WARNING, logger="pitstop.reference"):
        result = get_reference_data("circuit", year=2024, name="Monaco")

    assert result.circuits is not None
    assert len(result.circuits) == 1
    assert result.circuits[0].circuit_name == "Circuit de Monaco"
    assert result.circuits[0].corners is None  # No enrichment, but circuit returned
    assert any("enrichment" in r.message.lower() for r in caplog.records)


@patch("pitstop.tools.reference.reference.fastf1_client")
def test_tire_compounds_no_external_call(mock_client):
    result = get_reference_data("tire_compounds")

    mock_client.ergast.get_driver_info.assert_not_called()
    assert result.tire_compounds is not None
    assert len(result.tire_compounds) == 5
    names = {t.compound_name for t in result.tire_compounds}
    assert names == {"SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"}


@patch("pitstop.tools.reference.reference.fastf1_client")
def test_tire_compounds_pagination(mock_client):
    result = get_reference_data("tire_compounds", page=1, page_size=3)

    assert result.tire_compounds is not None
    assert len(result.tire_compounds) == 3
    assert result.pagination is not None
    assert result.pagination.total_items == 5
    assert result.pagination.total_pages == 2

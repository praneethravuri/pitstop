"""Tests for src/pitstop/clients/jolpica_client.py."""

import pytest

import pitstop.clients as clients_mod
from pitstop.clients.jolpica_client import (
    get_circuits,
    get_constructors,
    get_drivers,
    get_seasons,
    query,
)
from pitstop.exceptions import DataSourceError

MRDATA = {"MRData": {"RaceTable": {"Races": []}}}


@pytest.fixture(autouse=True)
def reset_singleton():
    clients_mod._jolpica_client = None
    yield
    clients_mod._jolpica_client = None


def test_query_makes_get_to_correct_url(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    query("2024/drivers")
    req = httpx_mock.get_requests()[0]
    assert str(req.url) == "https://api.jolpi.ca/ergast/f1/2024/drivers.json"


def test_query_returns_raw_dict(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    result = query("2024/drivers")
    assert result == MRDATA


def test_query_drops_none_params(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    query("2024/drivers", limit=None, offset=5)
    req = httpx_mock.get_requests()[0]
    assert "limit" not in str(req.url)
    assert "offset=5" in str(req.url)


def test_query_raises_data_source_error_on_4xx(httpx_mock):
    httpx_mock.add_response(status_code=404)
    with pytest.raises(DataSourceError) as exc_info:
        query("2024/drivers")
    assert "jolpica" in str(exc_info.value)


def test_query_raises_data_source_error_on_5xx(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with pytest.raises(DataSourceError) as exc_info:
        query("2024/circuits")
    assert "jolpica" in str(exc_info.value)


def test_get_circuits_calls_correct_path(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    result = get_circuits(2024)
    assert result == MRDATA
    req = httpx_mock.get_requests()[0]
    assert "2024/circuits.json" in str(req.url)


def test_get_drivers_calls_correct_path(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    get_drivers(2024)
    req = httpx_mock.get_requests()[0]
    assert "2024/drivers.json" in str(req.url)


def test_get_constructors_calls_correct_path(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    get_constructors(2024)
    req = httpx_mock.get_requests()[0]
    assert "2024/constructors.json" in str(req.url)


def test_get_seasons_calls_correct_path(httpx_mock):
    httpx_mock.add_response(json=MRDATA)
    get_seasons()
    req = httpx_mock.get_requests()[0]
    assert "seasons.json" in str(req.url)

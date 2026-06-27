"""Tests for src/pitstop/clients/wikidata_client.py."""

import pytest

from pitstop.clients import wikidata_client as wikidata_mod
from pitstop.clients.wikidata_client import run_sparql
from pitstop.exceptions import DataSourceError


@pytest.fixture(autouse=True)
def reset_client():
    wikidata_mod._client = None
    yield
    wikidata_mod._client = None


def test_run_sparql_select_returns_flattened_rows(httpx_mock):
    httpx_mock.add_response(
        json={
            "results": {
                "bindings": [
                    {
                        "driver": {"value": "http://www.wikidata.org/entity/Q9696"},
                        "name": {"value": "Lewis Hamilton"},
                    },
                    {
                        "driver": {"value": "http://www.wikidata.org/entity/Q10096"},
                        "name": {"value": "Max Verstappen"},
                    },
                ]
            }
        }
    )
    result = run_sparql("SELECT ?driver ?name WHERE { ?driver wdt:P31 wd:Q5 } LIMIT 2")
    assert result == [
        {"driver": "http://www.wikidata.org/entity/Q9696", "name": "Lewis Hamilton"},
        {"driver": "http://www.wikidata.org/entity/Q10096", "name": "Max Verstappen"},
    ]


def test_run_sparql_ask_returns_boolean_row(httpx_mock):
    httpx_mock.add_response(json={"boolean": True})
    result = run_sparql("ASK { wd:Q9696 wdt:P31 wd:Q5 }")
    assert result == [{"boolean": "true"}]


def test_http_error_raises_data_source_error(httpx_mock):
    httpx_mock.add_response(status_code=500)
    with pytest.raises(DataSourceError) as exc_info:
        run_sparql("SELECT ?x WHERE { ?x ?y ?z } LIMIT 1")
    assert "wikidata" in str(exc_info.value)


def test_user_agent_header_is_set(httpx_mock):
    httpx_mock.add_response(json={"results": {"bindings": []}})
    run_sparql("SELECT ?x WHERE { ?x ?y ?z } LIMIT 1")
    req = httpx_mock.get_requests()[0]
    assert "pitstop-mcp" in req.headers.get("user-agent", "")

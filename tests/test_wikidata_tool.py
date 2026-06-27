"""Tests for tools/wikidata/wikidata.py."""

from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.exceptions import DataSourceError
from pitstop.tools.wikidata.wikidata import query_wikidata


def _rows(n: int) -> list[dict]:
    return [{"driver": f"http://wikidata.org/entity/Q{i}", "name": f"Driver {i}"} for i in range(n)]


@patch("pitstop.tools.wikidata.wikidata.wikidata_client")
def test_select_query_returns_paginated_response(mock_client):
    mock_client.run_sparql.return_value = _rows(3)
    result = query_wikidata("SELECT ?driver ?name WHERE { ?driver wdt:P31 wd:Q5 } LIMIT 3")
    assert len(result.rows) == 3
    assert result.row_count == 3
    assert result.pagination is not None
    assert result.pagination.total_items == 3


@patch("pitstop.tools.wikidata.wikidata.wikidata_client")
def test_non_select_query_raises_tool_error(mock_client):
    with pytest.raises(ToolError):
        query_wikidata("INSERT INTO { ?x ?y ?z }")
    mock_client.run_sparql.assert_not_called()


@patch("pitstop.tools.wikidata.wikidata.wikidata_client")
def test_update_query_raises_tool_error(mock_client):
    with pytest.raises(ToolError):
        query_wikidata("UPDATE { ?x ?y ?z }")
    mock_client.run_sparql.assert_not_called()


@patch("pitstop.tools.wikidata.wikidata.wikidata_client")
def test_ask_query_allowed(mock_client):
    mock_client.run_sparql.return_value = [{"boolean": "true"}]
    result = query_wikidata("ASK { wd:Q9696 wdt:P31 wd:Q5 }")
    assert result.rows == [{"boolean": "true"}]
    mock_client.run_sparql.assert_called_once()


@patch("pitstop.tools.wikidata.wikidata.wikidata_client")
def test_data_source_error_raises_tool_error(mock_client):
    mock_client.run_sparql.side_effect = DataSourceError("wikidata", "sparql", "timeout")
    with pytest.raises(ToolError):
        query_wikidata("SELECT ?x WHERE { ?x ?y ?z } LIMIT 1")

"""Tests for tools/f1db/f1db.py."""

from unittest.mock import patch

import pytest
from fastmcp.exceptions import ToolError

from pitstop.exceptions import DataSourceError
from pitstop.tools.f1db.f1db import query_f1_database


def _rows(n: int) -> list[dict]:
    return [{"id": f"driver-{i}", "name": f"Driver {i}"} for i in range(n)]


@patch("pitstop.tools.f1db.f1db.get_f1db_client")
def test_select_query_returns_paginated_response(mock_get_client):
    mock_get_client.return_value.query.return_value = _rows(3)
    result = query_f1_database("SELECT id, name FROM driver LIMIT 3")
    assert len(result.rows) == 3
    assert result.row_count == 3
    assert result.pagination is not None
    assert result.pagination.total_items == 3


@patch("pitstop.tools.f1db.f1db.get_f1db_client")
def test_with_cte_query_allowed(mock_get_client):
    mock_get_client.return_value.query.return_value = _rows(1)
    result = query_f1_database("WITH d AS (SELECT * FROM driver) SELECT * FROM d")
    assert result.rows == _rows(1)
    mock_get_client.return_value.query.assert_called_once()


@patch("pitstop.tools.f1db.f1db.get_f1db_client")
def test_leading_line_comment_before_select_is_accepted(mock_get_client):
    mock_get_client.return_value.query.return_value = _rows(1)
    result = query_f1_database("-- x\nSELECT * FROM driver")
    assert result.rows == _rows(1)
    mock_get_client.return_value.query.assert_called_once()


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO driver (id) VALUES ('x')",
        "UPDATE driver SET name = 'x'",
        "PRAGMA table_info(driver)",
        "ATTACH DATABASE 'x' AS y",
        "DROP TABLE driver",
    ],
)
@patch("pitstop.tools.f1db.f1db.get_f1db_client")
def test_non_select_query_raises_tool_error(mock_get_client, sql):
    with pytest.raises(ToolError):
        query_f1_database(sql)
    mock_get_client.return_value.query.assert_not_called()


@patch("pitstop.tools.f1db.f1db.get_f1db_client")
def test_data_source_error_raises_tool_error(mock_get_client):
    mock_get_client.return_value.query.side_effect = DataSourceError("f1db", "query", "locked")
    with pytest.raises(ToolError):
        query_f1_database("SELECT * FROM driver")

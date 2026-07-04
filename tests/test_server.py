"""Tests for server.py: build_server() and main() importability."""

import pytest
from fastmcp import FastMCP

from pitstop.server import build_server, main


def test_build_server_returns_fastmcp():
    mcp = build_server()
    assert isinstance(mcp, FastMCP)


@pytest.mark.asyncio
async def test_all_tools_registered():
    mcp = build_server()
    tools = await mcp.list_tools()
    names = {t.name for t in tools}
    expected = {
        "get_session_data",
        "get_telemetry_data",
        "get_live_data",
        "get_standings",
        "get_schedule",
        "get_reference_data",
        "get_f1_news",
        "get_results",
        "get_race_analysis",
        "query_wikidata",
    }
    assert names == expected, f"tool mismatch: got {names}, expected {expected}"


def test_main_is_callable():
    # Just confirm it's importable and callable (don't actually run the server)
    assert callable(main)

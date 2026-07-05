"""Tests for health.py: check_health() with mocked HTTP."""

import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pitstop.health import check_health


def _mock_response(status_code: int = 200) -> MagicMock:
    r = MagicMock()
    r.raise_for_status = (
        MagicMock() if status_code < 400 else MagicMock(side_effect=Exception("HTTP error"))
    )
    return r


def _make_f1db(tmp_path) -> str:
    """Create a valid tiny sqlite db under a fresh subdir, return the cache dir."""
    cache_dir = tmp_path / "f1db_cache"
    cache_dir.mkdir()
    con = sqlite3.connect(cache_dir / "f1db.db")
    con.execute("CREATE TABLE t (x INTEGER)")
    con.close()
    return str(cache_dir)


@pytest.mark.asyncio
async def test_all_sources_ok(tmp_path):
    ok_resp = _mock_response(200)

    async def fake_get(url, **kwargs):
        return ok_resp

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("pitstop.health.httpx.AsyncClient", return_value=mock_client),
        patch("pitstop.health.os.environ.get", return_value=str(tmp_path)),
        patch("pitstop.health.os.makedirs"),
        patch("pitstop.health.tempfile.NamedTemporaryFile"),
        patch("pitstop.health.F1DB_CACHE_DIR", _make_f1db(tmp_path)),
    ):
        result = await check_health()

    assert result["overall"] == "ok"
    assert all(s["status"] == "ok" for s in result["sources"])


@pytest.mark.asyncio
async def test_one_source_down_gives_down(tmp_path):
    """If any HTTP probe raises, that source is 'down' and overall is 'down'."""

    call_count = 0

    async def fake_get(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if "jolpi" in url:
            raise Exception("ConnectionError")
        return _mock_response(200)

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("pitstop.health.httpx.AsyncClient", return_value=mock_client),
        patch("pitstop.health.os.environ.get", return_value=str(tmp_path)),
        patch("pitstop.health.os.makedirs"),
        patch("pitstop.health.tempfile.NamedTemporaryFile"),
        patch("pitstop.health.F1DB_CACHE_DIR", _make_f1db(tmp_path)),
    ):
        result = await check_health()

    jolpica = next(s for s in result["sources"] if s["name"] == "jolpica")
    assert jolpica["status"] == "down"
    assert result["overall"] == "down"


@pytest.mark.asyncio
async def test_fastf1_degraded_gives_degraded(tmp_path):
    """If only fastf1 cache is unwritable, overall is 'degraded'."""
    ok_resp = _mock_response(200)

    async def fake_get(url, **kwargs):
        return ok_resp

    mock_client = AsyncMock()
    mock_client.get = fake_get
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("pitstop.health.httpx.AsyncClient", return_value=mock_client),
        patch("pitstop.health.os.makedirs", side_effect=PermissionError("no write")),
        patch("pitstop.health.F1DB_CACHE_DIR", _make_f1db(tmp_path)),
    ):
        result = await check_health()

    fastf1 = next(s for s in result["sources"] if s["name"] == "fastf1")
    assert fastf1["status"] == "degraded"
    assert result["overall"] == "degraded"


def test_probe_f1db_degraded_when_db_missing(tmp_path):
    """Not-yet-downloaded is degraded (10/11 tools still work), not down."""
    from pitstop.health import _probe_f1db

    with patch("pitstop.health.F1DB_CACHE_DIR", str(tmp_path / "missing")):
        status = _probe_f1db()

    assert status["status"] == "degraded"


def test_probe_f1db_ok_when_db_present(tmp_path):
    from pitstop.health import _probe_f1db

    cache_dir = _make_f1db(tmp_path)
    with patch("pitstop.health.F1DB_CACHE_DIR", cache_dir):
        status = _probe_f1db()

    assert status["status"] == "ok"

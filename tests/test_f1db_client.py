"""Tests for src/pitstop/clients/f1db_client.py."""

import io
import os
import sqlite3
import time
import zipfile

import httpx
import pytest

from pitstop.clients.f1db_client import F1DBClient
from pitstop.exceptions import DataSourceError

_DB_URL = "https://example.com/f1db.zip"


def _zip_db_bytes(value: int = 1) -> bytes:
    """Build a tiny sqlite db (table t with one row) zipped as f1db.db."""
    # sqlite3 needs a real path, so use a temp file
    import tempfile

    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
        con = sqlite3.connect(path)
        con.execute("CREATE TABLE t (x INTEGER)")
        con.execute("INSERT INTO t VALUES (?)", (value,))
        con.commit()
        con.close()
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.write(path, arcname="f1db.db")
        return buf.getvalue()
    finally:
        os.remove(path)


def _write_local_db(
    cache_dir,
    value: int = 1,
    etag: str = '"etag-1"',
    last_modified: str = "Mon, 01 Jan 2024 00:00:00 GMT",
    age_seconds: float = 0,
):
    """Pre-populate cache_dir with a valid db + sidecar, as if already downloaded."""
    db_path = os.path.join(cache_dir, "f1db.db")
    con = sqlite3.connect(db_path)
    con.execute("CREATE TABLE t (x INTEGER)")
    con.execute("INSERT INTO t VALUES (?)", (value,))
    con.commit()
    con.close()
    sidecar_path = db_path + ".etag"
    with open(sidecar_path, "w") as f:
        f.write(f"{etag}\n{last_modified}\n")
    if age_seconds:
        old = time.time() - age_seconds
        os.utime(sidecar_path, (old, old))
    return db_path, sidecar_path


def test_ensure_db_downloads_and_writes_sidecar(tmp_path, httpx_mock):
    httpx_mock.add_response(
        content=_zip_db_bytes(),
        headers={"etag": '"abc"', "last-modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
    )
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    client._ensure_db()

    db_path = tmp_path / "f1db.db"
    sidecar_path = tmp_path / "f1db.db.etag"
    assert db_path.exists()
    assert sidecar_path.exists()
    assert sidecar_path.read_text() == '"abc"\nMon, 01 Jan 2024 00:00:00 GMT\n'


def test_fresh_sidecar_means_no_http_on_second_call(tmp_path, httpx_mock):
    httpx_mock.add_response(
        content=_zip_db_bytes(),
        headers={"etag": '"abc"', "last-modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
    )
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    client._ensure_db()
    client._ensure_db()  # sidecar is fresh; must not make another HTTP call

    assert len(httpx_mock.get_requests()) == 1


def test_stale_sidecar_unchanged_etag_skips_redownload(tmp_path, httpx_mock):
    db_path, sidecar_path = _write_local_db(str(tmp_path), value=1, age_seconds=100_000)
    httpx_mock.add_response(
        method="HEAD",
        headers={"etag": '"etag-1"', "last-modified": "Mon, 01 Jan 2024 00:00:00 GMT"},
    )
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    old_mtime = os.path.getmtime(sidecar_path)
    client._ensure_db()

    requests = httpx_mock.get_requests()
    assert len(requests) == 1
    assert requests[0].method == "HEAD"
    # sidecar touched, db content untouched
    assert os.path.getmtime(sidecar_path) >= old_mtime
    assert client.query("SELECT x FROM t") == [{"x": 1}]


def test_stale_sidecar_changed_etag_redownloads(tmp_path, httpx_mock):
    _write_local_db(str(tmp_path), value=1, etag='"etag-1"', age_seconds=100_000)
    httpx_mock.add_response(
        method="HEAD",
        headers={"etag": '"etag-2"', "last-modified": "Tue, 02 Jan 2024 00:00:00 GMT"},
    )
    httpx_mock.add_response(
        content=_zip_db_bytes(value=99),
        headers={"etag": '"etag-2"', "last-modified": "Tue, 02 Jan 2024 00:00:00 GMT"},
    )
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    client._ensure_db()

    methods = [r.method for r in httpx_mock.get_requests()]
    assert methods == ["HEAD", "GET"]
    assert client.query("SELECT x FROM t") == [{"x": 99}]


def test_head_network_error_with_local_db_serves_local(tmp_path, httpx_mock):
    _write_local_db(str(tmp_path), value=42, age_seconds=100_000)
    httpx_mock.add_exception(httpx.ConnectError("boom"), method="HEAD")
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    rows = client.query("SELECT x FROM t")

    assert rows == [{"x": 42}]


def test_no_local_db_and_download_fails_raises_data_source_error(tmp_path, httpx_mock):
    httpx_mock.add_exception(httpx.ConnectError("boom"), method="GET")
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    with pytest.raises(DataSourceError):
        client.query("SELECT 1")


def test_query_returns_list_of_dicts(tmp_path):
    _write_local_db(str(tmp_path), value=7)
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    rows = client.query("SELECT x FROM t")

    assert rows == [{"x": 7}]


def test_query_write_fails_due_to_read_only_mode(tmp_path):
    _write_local_db(str(tmp_path), value=1)
    client = F1DBClient(cache_dir=str(tmp_path), db_url=_DB_URL)

    with pytest.raises(DataSourceError):
        client.query("INSERT INTO t VALUES (2)")

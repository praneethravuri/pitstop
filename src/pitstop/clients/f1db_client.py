"""F1DB SQLite client — owned F1 database (1950-present).

Manages a local cache of ``f1db.db`` downloaded from a fixed GitHub release
asset, refreshed periodically by comparing ETag/Last-Modified, and exposes a
read-only ``query()`` used by the ``query_f1_database`` tool.
"""

import logging
import os
import shutil
import sqlite3
import tempfile
import time
import zipfile

import httpx

from pitstop.clients.http import make_client
from pitstop.config import F1DB_CACHE_DIR, F1DB_DB_URL, F1DB_UPDATE_CHECK_SECONDS
from pitstop.exceptions import DataSourceError

logger = logging.getLogger("pitstop.f1db")

_DB_FILENAME = "f1db.db"
_SIDECAR_SUFFIX = ".etag"
_QUERY_TIMEOUT_S = 15.0  # abort a pathological query (e.g. a giant cross join) after this long
_FETCH_CAP = 1001  # tools/f1db/f1db.py imports this; its _MAX_ROWS truncation is _FETCH_CAP - 1


class F1DBClient:
    """Downloads/refreshes the local f1db.db cache and runs read-only queries."""

    def __init__(self, cache_dir: str = F1DB_CACHE_DIR, db_url: str = F1DB_DB_URL) -> None:
        self._cache_dir = cache_dir
        self._db_url = db_url
        self._db_path = os.path.join(cache_dir, _DB_FILENAME)
        self._sidecar_path = self._db_path + _SIDECAR_SUFFIX

    def _read_sidecar(self) -> tuple[str | None, str | None]:
        try:
            with open(self._sidecar_path) as f:
                etag, last_modified = (f.readline().rstrip("\n"), f.readline().rstrip("\n"))
                return etag or None, last_modified or None
        except OSError:
            return None, None

    def _write_sidecar(self, etag: str | None, last_modified: str | None) -> None:
        with open(self._sidecar_path, "w") as f:
            f.write(f"{etag or ''}\n{last_modified or ''}\n")

    def _touch_sidecar(self) -> None:
        open(self._sidecar_path, "a").close()  # create-if-missing, then bump mtime
        os.utime(self._sidecar_path, None)

    def _download(self) -> None:
        """Stream-download the release zip, extract f1db.db, write the sidecar."""
        os.makedirs(self._cache_dir, exist_ok=True)
        client = make_client(follow_redirects=True)
        tmp_zip_path = None
        try:
            with client.stream("GET", self._db_url) as response:
                response.raise_for_status()
                fd, tmp_zip_path = tempfile.mkstemp(dir=self._cache_dir, suffix=".zip")
                with os.fdopen(fd, "wb") as tmp:
                    for chunk in response.iter_bytes():
                        tmp.write(chunk)
                etag = response.headers.get("etag")
                last_modified = response.headers.get("last-modified")

            tmp_db_fd, tmp_db_path = tempfile.mkstemp(dir=self._cache_dir)
            os.close(tmp_db_fd)
            try:
                with (
                    zipfile.ZipFile(tmp_zip_path) as zf,
                    zf.open(_DB_FILENAME) as src,
                    open(tmp_db_path, "wb") as dst,
                ):
                    shutil.copyfileobj(src, dst)
                os.replace(tmp_db_path, self._db_path)
            except BaseException:
                os.remove(tmp_db_path)
                raise
        except (httpx.HTTPError, OSError, zipfile.BadZipFile, KeyError) as e:
            # covers network errors AND corrupt zip / missing member / disk-full,
            # so callers get the same DataSourceError → serve-local fallback
            raise DataSourceError("f1db", "download", str(e)) from e
        finally:
            client.close()
            if tmp_zip_path and os.path.exists(tmp_zip_path):
                os.remove(tmp_zip_path)

        self._write_sidecar(etag, last_modified)
        logger.info("[pitstop.f1db] downloaded f1db.db from %s", self._db_url)

    def _check_fresh(self) -> None:
        """HEAD the release URL; re-download only if ETag/Last-Modified changed."""
        etag, last_modified = self._read_sidecar()
        client = make_client(follow_redirects=True)
        try:
            response = client.head(self._db_url)
            response.raise_for_status()
            remote_etag = response.headers.get("etag")
            remote_last_modified = response.headers.get("last-modified")
        except httpx.HTTPError as e:
            logger.warning("[pitstop.f1db] freshness check failed, serving local copy: %s", e)
            self._touch_sidecar()
            return
        finally:
            client.close()

        if remote_etag != etag or remote_last_modified != last_modified:
            logger.info("[pitstop.f1db] remote db changed, re-downloading")
            try:
                self._download()
            except DataSourceError as e:
                logger.warning("[pitstop.f1db] re-download failed, serving local copy: %s", e)
                self._touch_sidecar()
        else:
            self._touch_sidecar()

    def _ensure_db(self) -> None:
        if not os.path.exists(self._db_path):
            self._download()
            return

        sidecar_age = (
            time.time() - os.path.getmtime(self._sidecar_path)
            if os.path.exists(self._sidecar_path)
            else float("inf")
        )
        # ponytail: no lock — two threadpool calls hitting a stale sidecar can
        # both re-download (atomic os.replace keeps it safe, just wasteful);
        # add a threading.Lock if double-downloads ever matter.
        if sidecar_age >= F1DB_UPDATE_CHECK_SECONDS:
            self._check_fresh()

    def query(self, sql: str) -> list[dict]:
        """Run a single SQL statement against f1db.db, return rows as plain dicts.

        Opens a fresh read-only connection per call (sqlite connections are
        cheap) — no shared state, so this is safe to call from FastMCP's
        threadpool without locking.
        """
        self._ensure_db()
        try:
            con = sqlite3.connect(
                f"file:{self._db_path}?mode=ro", uri=True, check_same_thread=False
            )
            con.row_factory = sqlite3.Row
            try:
                # sqlite3's execute() runs exactly one statement — this is the
                # multi-statement guard (a second `; DROP ...` etc. raises
                # ProgrammingError before mode=ro even gets a chance to reject it).
                deadline = time.monotonic() + _QUERY_TIMEOUT_S
                # Called every 100k VM instructions; returning truthy interrupts the
                # query, which sqlite3 surfaces as an OperationalError below.
                con.set_progress_handler(lambda: time.monotonic() > deadline, 100_000)
                cur = con.execute(sql)
                rows = cur.fetchmany(_FETCH_CAP)
            finally:
                con.close()
        except sqlite3.Error as e:
            raise DataSourceError("f1db", "query", str(e)) from e
        return [dict(row) for row in rows]

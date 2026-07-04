"""Health probes for Pitstop data sources."""

import asyncio
import logging
import os
import sqlite3
import tempfile
import time
from typing import TypedDict

import httpx

from pitstop import __version__
from pitstop.clients.f1db_client import _DB_FILENAME
from pitstop.config import F1DB_CACHE_DIR

logger = logging.getLogger("pitstop.health")


class SourceStatus(TypedDict):
    name: str
    status: str  # "ok" | "degraded" | "down"
    latency_ms: int
    detail: str


async def _probe_jolpica() -> SourceStatus:
    t = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get("https://api.jolpi.ca/ergast/f1/seasons.json", params={"limit": 1})
            r.raise_for_status()
        return {
            "name": "jolpica",
            "status": "ok",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "",
        }
    except Exception as e:
        return {
            "name": "jolpica",
            "status": "down",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": str(e),
        }


async def _probe_openf1() -> SourceStatus:
    t = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get("https://api.openf1.org/v1/meetings", params={"year": 2024})
            r.raise_for_status()
        return {
            "name": "openf1",
            "status": "ok",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "",
        }
    except Exception as e:
        return {
            "name": "openf1",
            "status": "down",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": str(e),
        }


async def _probe_rss() -> SourceStatus:
    t = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as c:
            r = await c.get("https://www.autosport.com/rss/f1/news")
            r.raise_for_status()
        return {
            "name": "rss",
            "status": "ok",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "",
        }
    except Exception as e:
        return {
            "name": "rss",
            "status": "degraded",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": str(e),
        }


def _probe_fastf1() -> SourceStatus:
    t = time.monotonic()
    try:
        cache_dir = os.environ.get("FASTF1_CACHE", "cache")
        os.makedirs(cache_dir, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=cache_dir, delete=True):
            pass
        return {
            "name": "fastf1",
            "status": "ok",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "cache writable",
        }
    except Exception as e:
        return {
            "name": "fastf1",
            "status": "degraded",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": str(e),
        }


def _probe_f1db() -> SourceStatus:
    t = time.monotonic()
    db_path = os.path.join(F1DB_CACHE_DIR, _DB_FILENAME)
    if not os.path.exists(db_path):
        return {
            "name": "f1db",
            "status": "down",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "database not downloaded yet",
        }
    try:
        # mode=ro: health checks must never trigger a download or write.
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            con.execute("SELECT 1")
        finally:
            con.close()
        return {
            "name": "f1db",
            "status": "ok",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": "",
        }
    except sqlite3.Error as e:
        return {
            "name": "f1db",
            "status": "down",
            "latency_ms": int((time.monotonic() - t) * 1000),
            "detail": str(e),
        }


async def check_health() -> dict:
    """Concurrently probe all data sources. Returns health dict."""
    fastf1_status = _probe_fastf1()
    f1db_status = _probe_f1db()
    jolpica_status, openf1_status, rss_status = await asyncio.gather(
        _probe_jolpica(), _probe_openf1(), _probe_rss()
    )
    sources = [fastf1_status, f1db_status, jolpica_status, openf1_status, rss_status]
    if any(s["status"] == "down" for s in sources):
        overall = "down"
    elif any(s["status"] != "ok" for s in sources):
        overall = "degraded"
    else:
        overall = "ok"
    return {"version": __version__, "overall": overall, "sources": sources}

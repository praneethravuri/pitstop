"""Jolpica (Ergast replacement) API client — thin wrapper over the shared httpx singleton."""

import logging
import time

import httpx

from pitstop.clients import get_jolpica_client
from pitstop.clients.http import http_retry
from pitstop.exceptions import DataSourceError
from pitstop.utils import drop_none

logger = logging.getLogger("pitstop.jolpica")


@http_retry()
def query(path: str, **params) -> dict:
    """GET https://api.jolpi.ca/ergast/f1/{path}.json — returns raw JSON dict."""
    client = get_jolpica_client()
    clean_params = drop_none(params)
    url = f"/{path}.json"
    logger.debug("[pitstop.jolpica] GET %s params=%s", url, clean_params)
    t = time.monotonic()
    try:
        r = client.get(url, params=clean_params)
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise DataSourceError("jolpica", path, str(e)) from e
    elapsed = int((time.monotonic() - t) * 1000)
    logger.debug("[pitstop.jolpica] GET %s -> %d (%dms)", url, r.status_code, elapsed)
    return r.json()


def get_seasons(**kw) -> dict:
    return query("seasons", **kw)


def get_circuits(season: int, **kw) -> dict:
    return query(f"{season}/circuits", **kw)


def get_drivers(season: int, **kw) -> dict:
    return query(f"{season}/drivers", **kw)


def get_constructors(season: int, **kw) -> dict:
    return query(f"{season}/constructors", **kw)

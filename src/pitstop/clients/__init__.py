"""Client factories and exports for the pitstop package."""

from pitstop.clients.http import make_client
from pitstop.config import CACHE_TTL_SECONDS, ENABLE_CACHING

from .fastf1_client import FastF1Client

_openf1_client = None
_jolpica_client = None


def get_openf1_client():
    """Return the shared OpenF1 httpx.Client singleton."""
    global _openf1_client
    if _openf1_client is None:
        _openf1_client = make_client(
            base_url="https://api.openf1.org/v1",
            timeout=30.0,
            cache_ttl=CACHE_TTL_SECONDS if ENABLE_CACHING else None,
        )
    return _openf1_client


def get_jolpica_client():
    """Return the shared Jolpica httpx.Client singleton."""
    global _jolpica_client
    if _jolpica_client is None:
        _jolpica_client = make_client(
            base_url="https://api.jolpi.ca/ergast/f1",
            timeout=30.0,
            cache_ttl=CACHE_TTL_SECONDS if ENABLE_CACHING else None,
        )
    return _jolpica_client


__all__ = [
    "FastF1Client",
    "make_client",
    "get_openf1_client",
    "get_jolpica_client",
]

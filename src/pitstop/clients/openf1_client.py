"""OpenF1 API client — module-level functions backed by the shared httpx singleton."""
import logging
import time

from pitstop.clients import get_openf1_client
from pitstop.utils import drop_none

logger = logging.getLogger("pitstop.openf1")


def query(endpoint: str, **filters) -> list[dict]:
    """Generic OpenF1 GET. Drops None filters, raises on non-2xx."""
    client = get_openf1_client()
    params = drop_none(filters)
    logger.debug("[pitstop.openf1] GET %s params=%s", endpoint, params)
    t = time.monotonic()
    response = client.get(endpoint, params=params)
    response.raise_for_status()
    elapsed = int((time.monotonic() - t) * 1000)
    logger.debug("[pitstop.openf1] GET %s -> %d (%dms)", endpoint, response.status_code, elapsed)
    return response.json()


def get_intervals(**kw) -> list[dict]: return query("/intervals", **kw)
def get_pit_stops(**kw) -> list[dict]: return query("/pit", **kw)
def get_team_radio(**kw) -> list[dict]: return query("/team_radio", **kw)
def get_stints(**kw) -> list[dict]: return query("/stints", **kw)
def get_race_control(**kw) -> list[dict]: return query("/race_control", **kw)
def get_sessions(**kw) -> list[dict]: return query("/sessions", **kw)
def get_meetings(**kw) -> list[dict]: return query("/meetings", **kw)
def get_location(**kw) -> list[dict]: return query("/location", **kw)
def get_car_data(**kw) -> list[dict]: return query("/car_data", **kw)

"""Wikidata SPARQL client — generic SELECT/ASK queries against the Wikidata Query Service."""

import logging
import time

import httpx

from pitstop import __version__
from pitstop.clients.http import http_retry, make_client
from pitstop.config import HTTP_CACHE_TTL
from pitstop.exceptions import DataSourceError

logger = logging.getLogger("pitstop.wikidata")

SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
_USER_AGENT = (
    f"pitstop-mcp/{__version__} (https://github.com/praneethravuri/pitstop; F1 MCP server)"
)
_TIMEOUT = 15.0

_client: httpx.Client | None = None


def get_wikidata_client() -> httpx.Client:
    """Lazy singleton httpx client for Wikidata."""
    global _client
    if _client is None:
        _client = make_client(
            base_url="",
            timeout=_TIMEOUT,
            cache_ttl=HTTP_CACHE_TTL,
        )
        _client.headers.update({"User-Agent": _USER_AGENT})
    return _client


@http_retry()
def run_sparql(sparql: str) -> list[dict]:
    """Execute a SPARQL SELECT or ASK query and return flattened rows."""
    client = get_wikidata_client()
    t = time.monotonic()
    logger.debug("[pitstop.wikidata] SPARQL query (%d chars)", len(sparql))
    try:
        r = client.get(
            SPARQL_ENDPOINT,
            params={"query": sparql, "format": "json"},
        )
        r.raise_for_status()
        data = r.json()
    except (httpx.HTTPStatusError, ValueError) as e:
        raise DataSourceError("wikidata", "sparql", str(e)) from e
    elapsed = int((time.monotonic() - t) * 1000)
    logger.debug("[pitstop.wikidata] SPARQL -> %d (%dms)", r.status_code, elapsed)
    if "boolean" in data:
        return [{"boolean": str(data["boolean"]).lower()}]
    bindings = data.get("results", {}).get("bindings", [])
    return [{k: v.get("value", "") for k, v in row.items()} for row in bindings]

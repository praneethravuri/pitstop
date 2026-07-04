"""Shared HTTP infrastructure: factory + retry decorator.

Hishel 1.3.0's transport integration (``hishel.httpx.SyncCacheTransport``)
wraps an ``httpx.BaseTransport`` and is passed straight into
``httpx.Client(transport=...)``, so caching is transparent to callers —
they just get a plain ``httpx.Client`` back.
"""

import logging
import sqlite3

import httpx
from hishel import BaseFilter, FilterPolicy, SyncSqliteStorage
from hishel.httpx import SyncCacheTransport
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from pitstop import __version__

logger = logging.getLogger("pitstop.http")


class _GetOnly(BaseFilter):
    """Only cache GET requests."""

    def needs_body(self) -> bool:
        return False

    def apply(self, item, body) -> bool:
        return item.method == "GET"


class _OkOnly(BaseFilter):
    """Only cache 200 responses."""

    def needs_body(self) -> bool:
        return False

    def apply(self, item, body) -> bool:
        return item.status_code == 200


def make_client(
    base_url: str = "",
    timeout: float = 30.0,
    cache_ttl: float | None = None,
    follow_redirects: bool = False,
) -> httpx.Client:
    """Create an httpx client with http2, a shared User-Agent, and optional caching.

    Args:
        base_url: Optional base URL prefix for all requests.
        timeout: Request timeout in seconds.
        cache_ttl: If set, cache GET/200 responses in memory for this many seconds.
        follow_redirects: Whether to follow HTTP redirects.

    Returns:
        A configured httpx.Client instance.
    """
    logger.debug(
        "Creating HTTP client for base_url=%r timeout=%s cache_ttl=%s",
        base_url,
        timeout,
        cache_ttl,
    )
    transport: httpx.BaseTransport = httpx.HTTPTransport(http2=True)
    if cache_ttl:
        # ponytail: in-memory cache lives as long as the process; switch to a
        # sqlite file if cold-start cost ever matters
        transport = SyncCacheTransport(
            transport,
            storage=SyncSqliteStorage(
                connection=sqlite3.connect(":memory:", check_same_thread=False),
                default_ttl=cache_ttl,
            ),
            policy=FilterPolicy(request_filters=[_GetOnly()], response_filters=[_OkOnly()]),
        )
    return httpx.Client(
        base_url=base_url,
        timeout=timeout,
        transport=transport,
        follow_redirects=follow_redirects,
        headers={"User-Agent": f"pitstop-mcp/{__version__}"},
    )


def http_retry(max_attempts: int = 3):
    """Return a tenacity retry decorator for transient HTTP failures.

    Retries on TimeoutException and ConnectError with exponential back-off
    (1 s, 2 s, 4 s … capped at 8 s). All other exceptions propagate
    immediately.

    Args:
        max_attempts: Maximum total attempts (default 3).

    Returns:
        A tenacity retry decorator.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )

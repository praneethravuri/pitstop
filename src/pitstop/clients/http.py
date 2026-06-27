"""Shared HTTP infrastructure: factory + retry decorator.

Hishel 1.3.0 ships a low-level proxy API that does not integrate with
httpx transports, so we fall back to plain httpx.Client with http2 and
a tenacity retry wrapper for transient failures as recommended in the
task brief.
"""

import httpx
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger("pitstop.http")


def make_client(base_url: str = "", timeout: float = 30.0) -> httpx.Client:
    """Create an httpx client with http2 and a shared User-Agent header.

    Args:
        base_url: Optional base URL prefix for all requests.
        timeout: Request timeout in seconds.

    Returns:
        A configured httpx.Client instance.
    """
    logger.debug("Creating HTTP client for base_url=%r timeout=%s", base_url, timeout)
    return httpx.Client(
        base_url=base_url,
        timeout=timeout,
        http2=True,
        headers={"User-Agent": "pitstop-mcp/0.2.0"},
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

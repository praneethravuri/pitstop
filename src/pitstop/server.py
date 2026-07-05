"""Pitstop F1 MCP server entry point."""

import asyncio
import logging
import time
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from starlette.requests import Request
from starlette.responses import JSONResponse

from pitstop.config import (
    HOST,
    LOG_FORMAT,
    LOG_LEVEL,
    PORT,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_PER_HOUR,
    TRANSPORT,
)
from pitstop.logging_setup import configure_logging
from pitstop.tools import (
    get_f1_news,
    get_live_data,
    get_race_analysis,
    get_reference_data,
    get_results,
    get_schedule,
    get_session_data,
    get_standings,
    get_telemetry_data,
    query_f1_database,
    query_wikidata,
)

logger = logging.getLogger("pitstop.server")

_TOOLS = [
    get_session_data,
    get_telemetry_data,
    get_live_data,
    get_standings,
    get_schedule,
    get_reference_data,
    get_f1_news,
    get_results,
    get_race_analysis,
    query_wikidata,
    query_f1_database,
]


# ponytail: FastMCP 3.4.2 has no named middleware (ErrorHandling/RateLimiting/Timing/Logging).
# Single class covers timing + logging. Add rate limiting via RateLimitingMiddleware
# if FastMCP ships it in a later release.
class TimingLoggingMiddleware(Middleware):
    """Log each tool call with elapsed time."""

    async def on_call_tool(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        t = time.monotonic()
        name = getattr(getattr(context.message, "params", None), "name", "unknown")
        try:
            result = await call_next(context)
            logger.info("tool=%s ms=%d", name, int((time.monotonic() - t) * 1000))
            return result
        except Exception:
            logger.exception("tool=%s failed ms=%d", name, int((time.monotonic() - t) * 1000))
            raise


class ConcurrencyLimitMiddleware(Middleware):
    """Limits concurrent tool calls, not per-second rate."""

    def __init__(self, max_concurrent: int) -> None:
        self._sem = asyncio.Semaphore(max_concurrent)

    async def on_call_tool(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        async with self._sem:
            return await call_next(context)


def build_server() -> FastMCP:
    mcp = FastMCP(
        "Pitstop F1",
        instructions=(
            "Formula 1 data server with 11 tools. "
            "Historical data (1950–present): get_results, get_standings, get_reference_data. "
            "FastF1 timing/telemetry (2018–present): get_session_data, get_telemetry_data, get_race_analysis. "
            "Live/real-time (2023–present): get_live_data. "
            "Schedule and news: get_schedule, get_f1_news. "
            "Wikidata SPARQL (all eras): query_wikidata. "
            "Owned F1 database SQL (1950–present): query_f1_database."
        ),
    )

    mcp.add_middleware(TimingLoggingMiddleware())
    if RATE_LIMIT_ENABLED:
        rps = max(1, RATE_LIMIT_PER_HOUR // 3600)
        mcp.add_middleware(ConcurrencyLimitMiddleware(max_concurrent=rps))

    for tool_fn in _TOOLS:
        mcp.tool(tool_fn)

    @mcp.custom_route("/", methods=["GET"])
    async def root(request: Request) -> JSONResponse:
        from pitstop import __version__

        return JSONResponse(
            {
                "name": "Pitstop F1 MCP Server",
                "version": __version__,
                "mcp_endpoint": "/mcp",
                "health": "/health",
                "docs": "https://github.com/praneethravuri/pitstop",
            }
        )

    @mcp.custom_route("/health", methods=["GET"])
    async def health_route(request: Request) -> JSONResponse:
        from pitstop.health import check_health

        result = await check_health()
        status_code = (
            200 if result["overall"] == "ok" else (503 if result["overall"] == "down" else 207)
        )
        return JSONResponse(result, status_code=status_code)

    @mcp.custom_route("/live", methods=["GET"])
    async def liveness(request: Request) -> JSONResponse:
        return JSONResponse({"status": "alive"})

    @mcp.custom_route("/ready", methods=["GET"])
    async def readiness(request: Request) -> JSONResponse:
        return JSONResponse({"status": "ready"})

    @mcp.resource("health://status")
    async def health_status() -> dict:
        from pitstop.health import check_health

        return await check_health()

    logger.info("[pitstop.server] built transport=%s host=%s port=%s", TRANSPORT, HOST, PORT)
    return mcp


def main() -> None:
    configure_logging(level=LOG_LEVEL, fmt=LOG_FORMAT)
    mcp = build_server()
    try:
        if TRANSPORT == "stdio":
            mcp.run(transport="stdio")
        else:
            try:
                import uvloop

                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            except ImportError:
                pass
            mcp.run(transport="http", host=HOST, port=PORT)
    except KeyboardInterrupt:
        logger.info("[pitstop.server] shutting down")


if __name__ == "__main__":
    main()

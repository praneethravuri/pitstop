"""Error helpers for converting exceptions into ToolError."""

import logging

from fastmcp.exceptions import ToolError

logger = logging.getLogger("pitstop.errors")


def to_tool_error(operation: str, source: str, exc: Exception, hint: str = "") -> ToolError:
    """Wrap any exception into a ToolError the agent can always read."""
    exc_type = type(exc).__name__
    msg = f"[{source}] {operation} failed: {exc_type}: {exc}"
    if hint:
        msg = f"{msg}. {hint}"
    logger.error(msg, exc_info=exc)
    return ToolError(msg)

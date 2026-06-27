"""Logging configuration for Pitstop. Always uses stderr — safe for stdio MCP."""

import logging
import sys

_TEXT_FORMAT = "[%(name)s] %(levelname)s: %(message)s"
_JSON_FORMAT = '{"level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}'


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """Configure root pitstop logger with a stderr handler."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter(_JSON_FORMAT if fmt == "json" else _TEXT_FORMAT))
    root = logging.getLogger("pitstop")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False

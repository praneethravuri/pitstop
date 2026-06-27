"""Logging configuration for Pitstop. Always uses stderr — safe for stdio MCP."""

import json
import logging
import sys

_TEXT_FORMAT = "[%(name)s] %(levelname)s: %(message)s"


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return json.dumps(
            {
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


def configure_logging(level: str = "INFO", fmt: str = "text") -> None:
    """Configure root pitstop logger with a stderr handler."""
    handler = logging.StreamHandler(sys.stderr)
    if fmt == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter(_TEXT_FORMAT))
    root = logging.getLogger("pitstop")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.handlers.clear()
    root.addHandler(handler)
    root.propagate = False

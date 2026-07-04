"""Configuration for Pitstop F1 MCP Server."""

import os

from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv("PITSTOP_ENV", "development")
LOG_LEVEL = os.getenv("PITSTOP_LOG_LEVEL", "DEBUG" if ENV == "development" else "INFO")
LOG_FORMAT = os.getenv("PITSTOP_LOG_FORMAT", "text" if ENV == "development" else "json")

RATE_LIMIT_ENABLED = os.getenv("PITSTOP_RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_PER_HOUR = int(os.getenv("PITSTOP_RATE_LIMIT_PER_HOUR", "3600"))

TRANSPORT = os.getenv("PITSTOP_TRANSPORT", "http")  # "http" | "stdio"
HOST = os.getenv("PITSTOP_HOST", "0.0.0.0")
PORT = int(os.getenv("PITSTOP_PORT", "8000"))

FASTF1_CACHE_DIR = os.getenv("FASTF1_CACHE", "cache")
ENABLE_CACHING = os.getenv("PITSTOP_ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("PITSTOP_CACHE_TTL_SECONDS", "300"))
# TTL to pass to make_client(): None disables HTTP response caching
HTTP_CACHE_TTL = CACHE_TTL_SECONDS if ENABLE_CACHING else None

"""
Configuration for Pitstop F1 MCP Server
Supports development and production environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Try to load from current directory as fallback
    load_dotenv()

# Environment configuration
ENV = os.getenv("PITSTOP_ENV", "development")  # development or production
LOG_LEVEL = os.getenv("PITSTOP_LOG_LEVEL", "INFO" if ENV == "production" else "DEBUG")

# Server configuration
SERVER_NAME = "Pitstop F1"
SERVER_VERSION = "1.0.0"

# Feature flags
ENABLE_CACHING = os.getenv("PITSTOP_ENABLE_CACHING", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("PITSTOP_CACHE_TTL", "300"))  # 5 minutes default

# Error handling
MASK_ERRORS_IN_PRODUCTION = ENV == "production"
DETAILED_ERROR_MESSAGES = ENV == "development"

# Rate limiting (requests per hour per client)
RATE_LIMIT_ENABLED = os.getenv("PITSTOP_RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_PER_HOUR = int(os.getenv("PITSTOP_RATE_LIMIT", "1000"))

# Timeout settings (seconds)
DEFAULT_TIMEOUT = int(os.getenv("PITSTOP_TIMEOUT", "30"))
TELEMETRY_TIMEOUT = int(os.getenv("PITSTOP_TELEMETRY_TIMEOUT", "60"))  # Telemetry can be slow

# Logging configuration
LOG_FORMAT = "json" if ENV == "production" else "text"
LOG_INCLUDE_TIMESTAMP = True
LOG_INCLUDE_REQUEST_ID = True

# Data source URLs (for monitoring/health checks)
DATA_SOURCES = {
    "fastf1": "FastF1 Library",
    "ergast": "http://ergast.com/api/f1",
    "openf1": "https://api.openf1.org/v1",
}


def get_config() -> dict:
    """Get current configuration as dictionary."""
    return {
        "environment": ENV,
        "server_name": SERVER_NAME,
        "server_version": SERVER_VERSION,
        "log_level": LOG_LEVEL,
        "caching_enabled": ENABLE_CACHING,
        "cache_ttl": CACHE_TTL_SECONDS,
        "rate_limiting_enabled": RATE_LIMIT_ENABLED,
        "mask_errors": MASK_ERRORS_IN_PRODUCTION,
    }


def is_production() -> bool:
    """Check if running in production mode."""
    return ENV == "production"


def is_development() -> bool:
    """Check if running in development mode."""
    return ENV == "development"

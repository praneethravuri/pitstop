"""Custom exceptions for Pitstop."""


class PitstopError(Exception):
    """Base exception for all Pitstop errors."""


class DataSourceError(PitstopError):
    """Raised when an upstream data source (FastF1, OpenF1, Jolpica, RSS) fails."""

    def __init__(self, source: str, operation: str, reason: str) -> None:
        self.source = source
        self.operation = operation
        self.reason = reason
        super().__init__(f"[{source}] {operation} failed: {reason}")


class InputValidationError(PitstopError):
    """Raised when input parameters fail validation (e.g. bad year, unknown session type)."""


class NetworkError(PitstopError):
    """Raised on connection failure, timeout, or DNS error to an upstream API."""


class ParseError(PitstopError):
    """Raised when an API response cannot be parsed into the expected structure."""


class RateLimitError(PitstopError):
    """Raised when an upstream API rate limit is exceeded after all retries."""


class CacheError(PitstopError):
    """Raised when the disk/memory cache is unavailable or corrupted."""


class SessionNotFoundError(PitstopError):
    """Raised when the requested F1 session does not exist in the data source."""

    def __init__(self, year: int, gp: str, session: str) -> None:
        self.year = year
        self.gp = gp
        self.session = session
        super().__init__(f"Session not found: {year} {gp} {session}")


class DriverNotFoundError(PitstopError):
    """Raised when a driver identifier cannot be resolved."""

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        super().__init__(f"Driver not found: {identifier}")


class ConfigurationError(PitstopError):
    """Raised when required configuration is missing or invalid at startup."""

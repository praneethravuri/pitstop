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


class ValidationError(PitstopError):
    """Raised when input parameters fail validation."""


class RateLimitError(PitstopError):
    """Raised when a rate limit is exceeded."""


class CacheError(PitstopError):
    """Raised when the cache layer encounters an error."""

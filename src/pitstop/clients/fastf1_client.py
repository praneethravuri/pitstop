import logging
from datetime import datetime
from pathlib import Path
from typing import Literal

import fastf1
from fastf1.ergast import Ergast

from pitstop.exceptions import DataSourceError

logger = logging.getLogger("pitstop.fastf1")


class FastF1Client:
    """
    FastF1 client for accessing Formula 1 data.

    This client provides core methods from the FastF1 API:
    - Session loading (get_session, get_testing_session)
    - Event information (get_event, get_testing_event)
    - Event schedules (get_event_schedule, get_events_remaining)
    - Historical F1 data via Ergast API

    For subsidiary functions like results, laps, telemetry, etc., see the tools/ directory.
    """

    def __init__(self, cache_dir: str = "cache", enable_cache: bool = True):
        """
        Initialize the FastF1 client.

        Args:
            cache_dir: Directory path for caching F1 data (default: "cache")
            enable_cache: Whether to enable caching (default: True)
        """
        self.cache_dir = Path(cache_dir)
        self.ergast = Ergast()

        # Setup cache if enabled
        if enable_cache:
            self.cache_dir.mkdir(exist_ok=True)
            fastf1.Cache.enable_cache(str(self.cache_dir))

    def get_session(
        self,
        year: int,
        gp: str | int,
        identifier: int | str | None = None,
        *,
        backend: Literal["fastf1", "f1timing", "ergast"] | None = None,
    ):
        """
        Get a session object for a specific event.

        Args:
            year: The season year
            gp: The Grand Prix name or round number
            identifier: Session identifier (e.g., 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R', or session number)
            backend: Data source backend ('fastf1', 'f1timing', or 'ergast')

        Returns:
            Session object (not loaded - call .load() to fetch data)

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If session creation fails

        Examples:
            >>> session = client.get_session(2024, 'Monza', 'Q')
            >>> session.load()
        """
        logger.debug(
            "[pitstop.fastf1] get_session year=%s gp=%s identifier=%s", year, gp, identifier
        )
        try:
            return fastf1.get_session(year, gp, identifier, backend=backend)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_session", str(e)) from e

    def get_testing_session(
        self,
        year: int,
        test_number: int,
        session_number: int,
        *,
        backend: Literal["fastf1", "f1timing"] | None = None,
    ):
        """
        Get a testing session object.

        Args:
            year: The season year
            test_number: The test number (e.g., 1, 2)
            session_number: The session number within the test (e.g., 1, 2, 3)
            backend: Data source backend ('fastf1' or 'f1timing')

        Returns:
            Session object (not loaded - call .load() to fetch data)

        Raises:
            RuntimeError: If session creation fails

        Examples:
            >>> session = client.get_testing_session(2024, 1, 2)
            >>> session.load()
        """
        logger.debug(
            "[pitstop.fastf1] get_testing_session year=%s test=%s session=%s",
            year,
            test_number,
            session_number,
        )
        try:
            return fastf1.get_testing_session(year, test_number, session_number, backend=backend)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_testing_session", str(e)) from e

    def get_event(
        self,
        year: int,
        gp: int | str,
        *,
        backend: Literal["fastf1", "f1timing", "ergast"] | None = None,
        exact_match: bool = False,
    ):
        """
        Get an event (Grand Prix) object.

        Args:
            year: The season year
            gp: The Grand Prix name or round number
            backend: Data source backend ('fastf1', 'f1timing', or 'ergast')
            exact_match: Whether to require exact name match (default: False)

        Returns:
            Event object with event details

        Raises:
            RuntimeError: If event fetch fails

        Examples:
            >>> event = client.get_event(2024, 'Monza')
            >>> event = client.get_event(2024, 1)  # Round number
        """
        logger.debug("[pitstop.fastf1] get_event year=%s gp=%s", year, gp)
        try:
            return fastf1.get_event(year, gp, backend=backend, exact_match=exact_match)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_event", str(e)) from e

    def get_testing_event(
        self,
        year: int,
        test_number: int,
        *,
        backend: Literal["fastf1", "f1timing"] | None = None,
    ):
        """
        Get a testing event object.

        Args:
            year: The season year
            test_number: The test number (e.g., 1, 2)
            backend: Data source backend ('fastf1' or 'f1timing')

        Returns:
            Event object for the testing event

        Raises:
            RuntimeError: If event fetch fails

        Examples:
            >>> event = client.get_testing_event(2024, 1)
        """
        logger.debug("[pitstop.fastf1] get_testing_event year=%s test=%s", year, test_number)
        try:
            return fastf1.get_testing_event(year, test_number, backend=backend)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_testing_event", str(e)) from e

    def get_events_remaining(
        self,
        dt: datetime | None = None,
        *,
        include_testing: bool = True,
        backend: Literal["fastf1", "f1timing", "ergast"] | None = None,
    ):
        """
        Get remaining events from a given date.

        Args:
            dt: The date to check from (default: current date/time)
            include_testing: Whether to include testing events (default: True)
            backend: Data source backend ('fastf1', 'f1timing', or 'ergast')

        Returns:
            EventSchedule object with remaining events

        Raises:
            RuntimeError: If fetch fails

        Examples:
            >>> remaining = client.get_events_remaining()
            >>> from datetime import datetime
            >>> remaining = client.get_events_remaining(datetime(2024, 6, 1))
        """
        logger.debug("[pitstop.fastf1] get_events_remaining dt=%s", dt)
        try:
            return fastf1.get_events_remaining(dt, include_testing=include_testing, backend=backend)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_events_remaining", str(e)) from e

    def get_event_schedule(
        self,
        year: int,
        *,
        include_testing: bool = True,
        backend: Literal["fastf1", "f1timing", "ergast"] | None = None,
    ):
        """
        Get the full event schedule for a season.

        Args:
            year: The season year
            include_testing: Whether to include testing events (default: True)
            backend: Data source backend ('fastf1', 'f1timing', or 'ergast')

        Returns:
            EventSchedule object with full season schedule

        Raises:
            RuntimeError: If schedule fetch fails

        Examples:
            >>> schedule = client.get_event_schedule(2024)
            >>> schedule = client.get_event_schedule(2024, include_testing=False)
        """
        logger.debug("[pitstop.fastf1] get_event_schedule year=%s", year)
        try:
            return fastf1.get_event_schedule(year, include_testing=include_testing, backend=backend)
        except Exception as e:
            logger.error("[pitstop.fastf1] failed: %s", e, exc_info=True)
            raise DataSourceError("fastf1", "get_event_schedule", str(e)) from e

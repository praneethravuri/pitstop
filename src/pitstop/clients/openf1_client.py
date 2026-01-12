"""
OpenF1 API Client - Real-time F1 data from OpenF1.org

API Documentation: https://openf1.org/
Base URL: https://api.openf1.org/v1/

Available endpoints:
- /car_data: Real-time telemetry (speed, throttle, brake, gear, RPM)
- /team_radio: Radio message transcripts with timestamps
- /pit: Pit stop data with crew timing
- /intervals: Real-time gaps between drivers
- /laps: Lap counting and completion
- /meetings: Session information
- /sessions: Session details
- /location: Driver position on circuit (X/Y/Z coordinates)
- /weather: Live weather during session
- /stints: Tire compound and stint tracking
- /race_control: Real-time race control messages
"""

import httpx
import time
from typing import Optional, Any
from datetime import datetime


class OpenF1Client:
    """Client for interacting with the OpenF1 API."""

    BASE_URL = "https://api.openf1.org/v1"

    def __init__(self, timeout: int = 30):
        """
        Initialize OpenF1 client.

        Args:
            timeout: Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def _get(self, endpoint: str, params: Optional[dict[str, Any]] = None, max_retries: int = 3) -> list[dict]:
        """
        Make GET request to OpenF1 API with retry logic.

        Args:
            endpoint: API endpoint (e.g., '/car_data')
            params: Query parameters
            max_retries: Maximum number of retry attempts for rate limiting (default: 3)

        Returns:
            List of dictionaries containing response data

        Raises:
            httpx.HTTPStatusError: If request fails after all retries
        """
        url = f"{self.BASE_URL}{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                response = self.client.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                # Handle rate limiting (429) with exponential backoff
                if e.response.status_code == 429 and attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    time.sleep(wait_time)
                    continue
                # Re-raise if not a rate limit error or out of retries
                raise

    def get_team_radio(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None,
        date_start: Optional[str] = None,
        date_end: Optional[str] = None
    ) -> list[dict]:
        """
        Get team radio messages with transcripts.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)
            date_start: Start datetime (ISO 8601 format)
            date_end: End datetime (ISO 8601 format)

        Returns:
            List of radio messages with date, driver_number, recording_url, meeting_key
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number
        if date_start:
            params['date>='] = date_start
        if date_end:
            params['date<='] = date_end

        return self._get('/team_radio', params)

    def get_pit_stops(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None,
        pit_duration_min: Optional[float] = None,
        pit_duration_max: Optional[float] = None
    ) -> list[dict]:
        """
        Get pit stop data with crew timing.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)
            pit_duration_min: Minimum pit duration in seconds
            pit_duration_max: Maximum pit duration in seconds

        Returns:
            List of pit stops with date, driver_number, lap_number, pit_duration, meeting_key
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number
        if pit_duration_min is not None:
            params['pit_duration>='] = pit_duration_min
        if pit_duration_max is not None:
            params['pit_duration<='] = pit_duration_max

        return self._get('/pit', params)

    def get_car_data(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None,
        speed_min: Optional[int] = None,
        speed_max: Optional[int] = None
    ) -> list[dict]:
        """
        Get real-time car telemetry data.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)
            speed_min: Minimum speed filter (km/h)
            speed_max: Maximum speed filter (km/h)

        Returns:
            List of telemetry points with brake, date, drs, gear, meeting_key, n_gear,
            rpm, session_key, speed, throttle
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number
        if speed_min is not None:
            params['speed>='] = speed_min
        if speed_max is not None:
            params['speed<='] = speed_max

        return self._get('/car_data', params)

    def get_intervals(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None
    ) -> list[dict]:
        """
        Get real-time gaps and intervals between drivers.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)

        Returns:
            List of interval data with date, driver_number, gap_to_leader, interval, meeting_key
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number

        return self._get('/intervals', params)

    def get_meetings(
        self,
        year: Optional[int] = None,
        country_name: Optional[str] = None,
        circuit_short_name: Optional[str] = None
    ) -> list[dict]:
        """
        Get meeting (race weekend) information.

        Args:
            year: Championship year
            country_name: Country name (e.g., 'Monaco')
            circuit_short_name: Circuit short name (e.g., 'Monaco')

        Returns:
            List of meetings with circuit info, country, date, location, year
        """
        params = {}
        if year:
            params['year'] = year
        if country_name:
            params['country_name'] = country_name
        if circuit_short_name:
            params['circuit_short_name'] = circuit_short_name

        return self._get('/meetings', params)

    def get_sessions(
        self,
        session_key: Optional[int] = None,
        session_name: Optional[str] = None,
        year: Optional[int] = None,
        country_name: Optional[str] = None
    ) -> list[dict]:
        """
        Get session details.

        Args:
            session_key: Unique identifier for session
            session_name: Session name (e.g., 'Race', 'Qualifying', 'Practice 1')
            year: Championship year
            country_name: Country name

        Returns:
            List of sessions with circuit info, date, location, session details
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if session_name:
            params['session_name'] = session_name
        if year:
            params['year'] = year
        if country_name:
            params['country_name'] = country_name

        return self._get('/sessions', params)

    def get_location(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None
    ) -> list[dict]:
        """
        Get driver position on circuit with X/Y/Z coordinates.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)

        Returns:
            List of location points with date, driver_number, meeting_key, x, y, z coordinates
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number

        return self._get('/location', params)

    def get_stints(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None,
        compound: Optional[str] = None
    ) -> list[dict]:
        """
        Get tire stint data.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)
            compound: Tire compound (e.g., 'SOFT', 'MEDIUM', 'HARD')

        Returns:
            List of stints with compound, driver_number, lap_start, lap_end, stint_number
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number
        if compound:
            params['compound'] = compound

        return self._get('/stints', params)

    def get_race_control(
        self,
        session_key: Optional[int] = None,
        driver_number: Optional[int] = None,
        flag: Optional[str] = None,
        category: Optional[str] = None
    ) -> list[dict]:
        """
        Get race control messages.

        Args:
            session_key: Unique identifier for session
            driver_number: Driver number (1-99)
            flag: Flag type (e.g., 'GREEN', 'YELLOW', 'RED', 'CHEQUERED')
            category: Message category (e.g., 'Flag', 'SafetyCar', 'Other')

        Returns:
            List of messages with category, date, driver_number, flag, lap_number, meeting_key, message, scope, sector, session_key
        """
        params = {}
        if session_key:
            params['session_key'] = session_key
        if driver_number:
            params['driver_number'] = driver_number
        if flag:
            params['flag'] = flag
        if category:
            params['category'] = category

        return self._get('/race_control', params)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Example usage
    client = OpenF1Client()

    # Get 2024 Monaco Grand Prix sessions
    meetings = client.get_meetings(year=2024, country_name="Monaco")
    print(f"Found {len(meetings)} meetings")

    if meetings:
        meeting = meetings[0]
        print(f"Meeting: {meeting.get('meeting_official_name')}")

        # Get sessions for this meeting
        sessions = client.get_sessions(year=2024, country_name="Monaco")
        print(f"\nSessions: {len(sessions)}")
        for session in sessions:
            print(f"  - {session.get('session_name')}: {session.get('date_start')}")

    client.close()

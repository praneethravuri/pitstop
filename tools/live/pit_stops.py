from clients.openf1_client import OpenF1Client
from typing import Optional
from models.live import PitStopsResponse, PitStopData

# Initialize OpenF1 client
openf1_client = OpenF1Client()


def get_live_pit_stops(
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: Optional[int] = None
) -> PitStopsResponse:
    """
    Get pit stop analysis with crew timing from OpenF1.

    Args:
        year: Season year (2023+, OpenF1 data availability)
        country: Country name (e.g., "Monaco", "Italy", "United States")
        session_name: Session name - 'Race', 'Qualifying', 'Sprint', 'Practice 1/2/3' (default: 'Race')
        driver_number: Optional filter by driver number (1-99)

    Returns:
        PitStopsResponse with pit stop durations and statistics

    Example:
        get_live_pit_stops(2024, "Monaco", "Race") → All pit stops with timing
        get_live_pit_stops(2024, "Monaco", "Race", 1) → Verstappen's pit stops
    """
    # Get meeting and session info
    meetings = openf1_client.get_meetings(year=year, country_name=country)
    if not meetings:
        return PitStopsResponse(
            session_name=session_name,
            year=year,
            country=country,
            pit_stops=[],
            total_pit_stops=0
        )

    # Get sessions for this meeting
    sessions = openf1_client.get_sessions(year=year, country_name=country, session_name=session_name)
    if not sessions:
        return PitStopsResponse(
            session_name=session_name,
            year=year,
            country=country,
            pit_stops=[],
            total_pit_stops=0
        )

    session = sessions[0]
    session_key = session['session_key']

    # Get pit stop data
    pit_data = openf1_client.get_pit_stops(
        session_key=session_key,
        driver_number=driver_number
    )

    # Convert to Pydantic models
    pit_stops = [
        PitStopData(
            date=stop['date'],
            driver_number=stop['driver_number'],
            lap_number=stop['lap_number'],
            pit_duration=stop['pit_duration'],
            session_key=stop['session_key'],
            meeting_key=stop['meeting_key']
        )
        for stop in pit_data
    ]

    # Calculate statistics
    fastest_stop = None
    slowest_stop = None
    average_duration = None

    if pit_stops:
        durations = [stop.pit_duration for stop in pit_stops]
        fastest_stop = min(durations)
        slowest_stop = max(durations)
        average_duration = sum(durations) / len(durations)

    return PitStopsResponse(
        session_name=session_name,
        year=year,
        country=country,
        pit_stops=pit_stops,
        total_pit_stops=len(pit_stops),
        fastest_stop=fastest_stop,
        slowest_stop=slowest_stop,
        average_duration=average_duration
    )


if __name__ == "__main__":
    # Test with 2024 Monaco GP
    print("Testing get_live_pit_stops with 2024 Monaco GP...")
    result = get_live_pit_stops(2024, "Monaco", "Race")
    print(f"Total pit stops: {result.total_pit_stops}")
    if result.fastest_stop:
        print(f"Fastest stop: {result.fastest_stop:.2f}s")
        print(f"Average stop: {result.average_duration:.2f}s")

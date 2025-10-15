from clients.openf1_client import OpenF1Client
from typing import Optional
from models.live import IntervalsResponse, IntervalData

# Initialize OpenF1 client
openf1_client = OpenF1Client()


def get_live_intervals(
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: Optional[int] = None
) -> IntervalsResponse:
    """
    Get real-time gaps and intervals between drivers from OpenF1.

    Args:
        year: Season year (2023+, OpenF1 data availability)
        country: Country name (e.g., "Monaco", "Italy", "United States")
        session_name: Session name - 'Race', 'Qualifying', 'Sprint', 'Practice 1/2/3' (default: 'Race')
        driver_number: Optional filter by driver number (1-99)

    Returns:
        IntervalsResponse with gap to leader and interval to car ahead

    Example:
        get_live_intervals(2024, "Monaco", "Race") → All intervals during race
        get_live_intervals(2024, "Monaco", "Race", 1) → Verstappen's gaps
    """
    # Get meeting and session info
    meetings = openf1_client.get_meetings(year=year, country_name=country)
    if not meetings:
        return IntervalsResponse(
            session_name=session_name,
            year=year,
            country=country,
            intervals=[],
            total_data_points=0
        )

    # Get sessions for this meeting
    sessions = openf1_client.get_sessions(year=year, country_name=country, session_name=session_name)
    if not sessions:
        return IntervalsResponse(
            session_name=session_name,
            year=year,
            country=country,
            intervals=[],
            total_data_points=0
        )

    session = sessions[0]
    session_key = session['session_key']

    # Get intervals data
    interval_data = openf1_client.get_intervals(
        session_key=session_key,
        driver_number=driver_number
    )

    # Convert to Pydantic models
    intervals = [
        IntervalData(
            date=data['date'],
            driver_number=data['driver_number'],
            gap_to_leader=data.get('gap_to_leader'),
            interval=data.get('interval'),
            session_key=data['session_key'],
            meeting_key=data['meeting_key']
        )
        for data in interval_data
    ]

    return IntervalsResponse(
        session_name=session_name,
        year=year,
        country=country,
        intervals=intervals,
        total_data_points=len(intervals)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco GP
    print("Testing get_live_intervals with 2024 Monaco GP...")
    result = get_live_intervals(2024, "Monaco", "Race")
    print(f"Total data points: {result.total_data_points}")
    if result.intervals:
        print(f"First interval: Driver {result.intervals[0].driver_number} - Gap: {result.intervals[0].gap_to_leader}")

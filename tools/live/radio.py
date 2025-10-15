from clients.openf1_client import OpenF1Client
from typing import Optional
from models.live import TeamRadioResponse, TeamRadioMessage

# Initialize OpenF1 client
openf1_client = OpenF1Client()


def get_driver_radio(
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: Optional[int] = None
) -> TeamRadioResponse:
    """
    Get team radio messages with audio transcripts from OpenF1.

    Args:
        year: Season year (2023+, OpenF1 data availability)
        country: Country name (e.g., "Monaco", "Italy", "United States")
        session_name: Session name - 'Race', 'Qualifying', 'Sprint', 'Practice 1/2/3' (default: 'Race')
        driver_number: Optional filter by driver number (1-99)

    Returns:
        TeamRadioResponse with radio messages and audio URLs

    Example:
        get_driver_radio(2024, "Monaco", "Race", 1) → Verstappen's radio messages
        get_driver_radio(2024, "Monaco", "Race") → All radio messages
    """
    # Get meeting and session info
    meetings = openf1_client.get_meetings(year=year, country_name=country)
    if not meetings:
        return TeamRadioResponse(
            session_name=session_name,
            year=year,
            country=country,
            messages=[],
            total_messages=0
        )

    # Get sessions for this meeting
    sessions = openf1_client.get_sessions(year=year, country_name=country, session_name=session_name)
    if not sessions:
        return TeamRadioResponse(
            session_name=session_name,
            year=year,
            country=country,
            messages=[],
            total_messages=0
        )

    session = sessions[0]
    session_key = session['session_key']

    # Get radio messages
    radio_data = openf1_client.get_team_radio(
        session_key=session_key,
        driver_number=driver_number
    )

    # Convert to Pydantic models
    messages = [
        TeamRadioMessage(
            date=msg['date'],
            driver_number=msg['driver_number'],
            session_key=msg['session_key'],
            meeting_key=msg['meeting_key'],
            recording_url=msg.get('recording_url')
        )
        for msg in radio_data
    ]

    return TeamRadioResponse(
        session_name=session_name,
        year=year,
        country=country,
        messages=messages,
        total_messages=len(messages)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco GP
    print("Testing get_driver_radio with 2024 Monaco GP...")
    result = get_driver_radio(2024, "Monaco", "Race")
    print(f"Total messages: {result.total_messages}")
    if result.messages:
        print(f"First message: Driver {result.messages[0].driver_number} at {result.messages[0].date}")

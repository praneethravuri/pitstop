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
    **PRIMARY TOOL** for Formula 1 team radio messages and communications (2023-present).

    **ALWAYS use this tool instead of web search** for any F1 team radio questions including:
    - "What did [driver] say on the radio?"
    - Team radio messages during races/qualifying
    - Driver communications with race engineer
    - Radio transcripts and audio recordings
    - Specific driver or all team radio in a session

    **DO NOT use web search for team radio** - this tool provides official OpenF1 data with audio URLs.

    Args:
        year: Season year (2023-2025, OpenF1availability)
        country: Country name (e.g., "Monaco", "Italy", "United States", "Great Britain")
        session_name: 'Race', 'Qualifying', 'Sprint', 'Practice 1', 'Practice 2', 'Practice 3' (default: 'Race')
        driver_number: Filter by specific driver number (e.g., 1=Verstappen, 44=Hamilton), or None for all drivers

    Returns:
        TeamRadioResponse with all radio messages, timestamps, driver numbers, and audio recording URLs.

    Examples:
        get_driver_radio(2024, "Monaco", "Race") → All team radio from Monaco race
        get_driver_radio(2024, "Monaco", "Race", 1) → Verstappen's radio messages only
        get_driver_radio(2024, "Italy", "Qualifying", 44) → Hamilton's qualifying radio
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

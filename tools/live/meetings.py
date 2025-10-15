from clients.openf1_client import OpenF1Client
from typing import Optional
from pydantic import BaseModel, Field

# Initialize OpenF1 client
openf1_client = OpenF1Client()


class SessionInfo(BaseModel):
    """Session information."""
    session_key: int = Field(..., description="Unique session identifier")
    session_name: str = Field(..., description="Session name (e.g., 'Race', 'Qualifying')")
    session_type: str = Field(..., description="Session type")
    date_start: str = Field(..., description="Session start datetime")
    date_end: str = Field(..., description="Session end datetime")
    gmt_offset: str = Field(..., description="GMT offset")
    circuit_key: int = Field(..., description="Circuit identifier")
    circuit_short_name: str = Field(..., description="Circuit short name")


class MeetingInfo(BaseModel):
    """Meeting (race weekend) information."""
    meeting_key: int = Field(..., description="Unique meeting identifier")
    meeting_name: str = Field(..., description="Official meeting name")
    meeting_official_name: str = Field(..., description="Full official name")
    location: str = Field(..., description="Location/city")
    country_name: str = Field(..., description="Country name")
    circuit_key: int = Field(..., description="Circuit identifier")
    circuit_short_name: str = Field(..., description="Circuit short name")
    date_start: str = Field(..., description="Meeting start date")
    year: int = Field(..., description="Year")


class MeetingResponse(BaseModel):
    """Response for meeting and session information."""
    meeting: Optional[MeetingInfo] = Field(None, description="Meeting information")
    sessions: list[SessionInfo] = Field(..., description="List of sessions in meeting")
    total_sessions: int = Field(..., description="Total number of sessions")


def get_meeting_info(
    year: int,
    country: str
) -> MeetingResponse:
    """
    Get meeting and session schedule information from OpenF1.

    Provides precise start times, session keys, and circuit details.

    Args:
        year: Season year (2023+, OpenF1 data availability)
        country: Country name (e.g., "Monaco", "Italy", "United States")

    Returns:
        MeetingResponse with meeting info and all sessions

    Example:
        get_meeting_info(2024, "Monaco") → Monaco GP weekend schedule
        get_meeting_info(2024, "Italy") → Italian GP at Monza
    """
    # Get meeting info
    meetings = openf1_client.get_meetings(year=year, country_name=country)
    if not meetings:
        return MeetingResponse(
            meeting=None,
            sessions=[],
            total_sessions=0
        )

    meeting_data = meetings[0]

    # Convert to Pydantic model
    meeting = MeetingInfo(
        meeting_key=meeting_data['meeting_key'],
        meeting_name=meeting_data['meeting_name'],
        meeting_official_name=meeting_data['meeting_official_name'],
        location=meeting_data['location'],
        country_name=meeting_data['country_name'],
        circuit_key=meeting_data['circuit_key'],
        circuit_short_name=meeting_data['circuit_short_name'],
        date_start=meeting_data['date_start'],
        year=meeting_data['year']
    )

    # Get sessions for this meeting
    sessions_data = openf1_client.get_sessions(year=year, country_name=country)

    # Convert sessions to Pydantic models
    sessions = [
        SessionInfo(
            session_key=session['session_key'],
            session_name=session['session_name'],
            session_type=session['session_type'],
            date_start=session['date_start'],
            date_end=session['date_end'],
            gmt_offset=session['gmt_offset'],
            circuit_key=session['circuit_key'],
            circuit_short_name=session['circuit_short_name']
        )
        for session in sessions_data
    ]

    return MeetingResponse(
        meeting=meeting,
        sessions=sessions,
        total_sessions=len(sessions)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco GP
    print("Testing get_meeting_info with 2024 Monaco GP...")
    result = get_meeting_info(2024, "Monaco")
    if result.meeting:
        print(f"Meeting: {result.meeting.meeting_official_name}")
        print(f"Location: {result.meeting.location}, {result.meeting.country_name}")
        print(f"\nSessions ({result.total_sessions}):")
        for session in result.sessions:
            print(f"  - {session.session_name}: {session.date_start}")

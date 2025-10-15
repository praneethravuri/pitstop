from clients.openf1_client import OpenF1Client
from typing import Optional
from pydantic import BaseModel, Field


# Initialize OpenF1 client
openf1_client = OpenF1Client()


class StintData(BaseModel):
    """Tire stint data."""
    stint_number: int = Field(..., description="Stint number")
    driver_number: int = Field(..., description="Driver number (1-99)")
    compound: str = Field(..., description="Tire compound (SOFT, MEDIUM, HARD, etc.)")
    lap_start: int = Field(..., description="Starting lap number")
    lap_end: int = Field(..., description="Ending lap number")
    tyre_age_at_start: int = Field(..., description="Tyre age at start of stint")


class StintsResponse(BaseModel):
    """Response for tire stint data."""
    session_name: Optional[str] = Field(None, description="Session name")
    year: Optional[int] = Field(None, description="Year")
    country: Optional[str] = Field(None, description="Country name")
    stints: list[StintData] = Field(..., description="List of tire stints")
    total_stints: int = Field(..., description="Total number of stints")


def get_stints_live(
    year: int,
    country: str,
    session_name: str = "Race",
    driver_number: Optional[int] = None,
    compound: Optional[str] = None
) -> StintsResponse:
    """
    Get real-time tire stint tracking from OpenF1.

    Args:
        year: Season year (2023+, OpenF1 data availability)
        country: Country name (e.g., "Monaco", "Italy", "United States")
        session_name: Session name - 'Race', 'Qualifying', 'Sprint', 'Practice 1/2/3' (default: 'Race')
        driver_number: Optional filter by driver number (1-99)
        compound: Optional filter by compound ('SOFT', 'MEDIUM', 'HARD', 'INTERMEDIATE', 'WET')

    Returns:
        StintsResponse with tire stint data

    Example:
        get_stints_live(2024, "Monaco", "Race") → All stints in race
        get_stints_live(2024, "Monaco", "Race", 1) → Verstappen's stints
        get_stints_live(2024, "Monaco", "Race", compound="SOFT") → All soft tire stints
    """
    # Get meeting and session info
    meetings = openf1_client.get_meetings(year=year, country_name=country)
    if not meetings:
        return StintsResponse(
            session_name=session_name,
            year=year,
            country=country,
            stints=[],
            total_stints=0
        )

    # Get sessions for this meeting
    sessions = openf1_client.get_sessions(year=year, country_name=country, session_name=session_name)
    if not sessions:
        return StintsResponse(
            session_name=session_name,
            year=year,
            country=country,
            stints=[],
            total_stints=0
        )

    session = sessions[0]
    session_key = session['session_key']

    # Get stint data
    stint_data = openf1_client.get_stints(
        session_key=session_key,
        driver_number=driver_number,
        compound=compound
    )

    # Convert to Pydantic models
    stints = [
        StintData(
            stint_number=stint['stint_number'],
            driver_number=stint['driver_number'],
            compound=stint['compound'],
            lap_start=stint['lap_start'],
            lap_end=stint['lap_end'],
            tyre_age_at_start=stint['tyre_age_at_start']
        )
        for stint in stint_data
    ]

    return StintsResponse(
        session_name=session_name,
        year=year,
        country=country,
        stints=stints,
        total_stints=len(stints)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco GP
    print("Testing get_stints_live with 2024 Monaco GP...")
    result = get_stints_live(2024, "Monaco", "Race")
    print(f"Total stints: {result.total_stints}")
    if result.stints:
        first = result.stints[0]
        print(f"First stint: Driver {first.driver_number}, {first.compound}, Laps {first.lap_start}-{first.lap_end}")

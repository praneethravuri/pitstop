from pydantic import BaseModel, Field
from datetime import datetime


class RaceEvent(BaseModel):
    """Single race event in the F1 calendar."""

    round_number: int = Field(..., description="Round number in the championship")
    race_name: str = Field(..., description="Official race name (e.g., 'Bahrain Grand Prix')")
    country: str = Field(..., description="Country where the race is held")
    location: str = Field(..., description="City/location of the circuit")
    circuit_name: str = Field(..., description="Official circuit name")
    date: str = Field(..., description="Race date (YYYY-MM-DD format)")


class RaceCalendar(BaseModel):
    """Complete F1 race calendar for a season."""

    year: int = Field(..., description="Championship season year")
    race_count: int = Field(..., description="Total number of races in the season")
    races: list[RaceEvent] = Field(..., description="List of all race events in the season")


class SessionInfo(BaseModel):
    """Information about a single session in a race weekend."""

    session_name: str = Field(..., description="Session name (Practice 1, Practice 2, Practice 3, Qualifying, Sprint, Race)")
    session_type: str = Field(..., description="Session type code (FP1, FP2, FP3, Q, S, R)")
    date: str = Field(..., description="Session date (YYYY-MM-DD)")
    time: str | None = Field(None, description="Session time (HH:MM format, if available)")


class WeekendSchedule(BaseModel):
    """Complete schedule for a race weekend."""

    year: int = Field(..., description="Season year")
    round_number: int = Field(..., description="Round number")
    race_name: str = Field(..., description="Race name")
    country: str = Field(..., description="Country")
    circuit_name: str = Field(..., description="Circuit name")
    sessions: list[SessionInfo] = Field(..., description="List of all sessions in the weekend")


class NextRaceInfo(BaseModel):
    """Information about the next upcoming race."""

    year: int = Field(..., description="Season year")
    round_number: int = Field(..., description="Round number")
    race_name: str = Field(..., description="Race name")
    country: str = Field(..., description="Country")
    location: str = Field(..., description="Location")
    circuit_name: str = Field(..., description="Circuit name")
    date: str = Field(..., description="Race date (YYYY-MM-DD)")
    days_until_race: int = Field(..., description="Number of days until the race")

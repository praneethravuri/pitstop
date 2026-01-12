from pydantic import BaseModel, Field
from typing import Optional


class EventInfo(BaseModel):
    """Information about an F1 event (race weekend or testing)."""

    round_number: Optional[int] = Field(None, description="Round number in the championship")
    event_name: str = Field(..., description="Name of the event (e.g., 'Italian Grand Prix')")
    country: str = Field(..., description="Country where the event takes place")
    location: str = Field(..., description="City/location of the circuit")
    official_event_name: Optional[str] = Field(None, description="Full official event name")
    event_date: Optional[str] = Field(None, description="Main event date")
    event_format: Optional[str] = Field(None, description="Event format (conventional, sprint, testing)")

    # Session times
    session_1_date: Optional[str] = Field(None, description="Session 1 date and time")
    session_2_date: Optional[str] = Field(None, description="Session 2 date and time")
    session_3_date: Optional[str] = Field(None, description="Session 3 date and time")
    session_4_date: Optional[str] = Field(None, description="Session 4 date and time")
    session_5_date: Optional[str] = Field(None, description="Session 5 date and time")

    # Session names
    session_1_name: Optional[str] = Field(None, description="Session 1 name")
    session_2_name: Optional[str] = Field(None, description="Session 2 name")
    session_3_name: Optional[str] = Field(None, description="Session 3 name")
    session_4_name: Optional[str] = Field(None, description="Session 4 name")
    session_5_name: Optional[str] = Field(None, description="Session 5 name")

    # Testing event indicator
    is_testing: bool = Field(default=False, description="Whether this is a testing event")


class ScheduleResponse(BaseModel):
    """Response containing F1 schedule information."""

    year: int = Field(..., description="Season year")
    total_events: int = Field(..., description="Total number of events")
    include_testing: bool = Field(..., description="Whether testing events are included")
    events: list[EventInfo] = Field(default_factory=list, description="List of events")

    # Optional filters applied
    round_filter: Optional[int] = Field(None, description="Round number filter (if applied)")
    event_name_filter: Optional[str] = Field(None, description="Event name filter (if applied)")
    only_remaining: bool = Field(default=False, description="Whether only remaining events are shown")

from pydantic import BaseModel, Field

from pitstop.models.common import PageMeta


class EventInfo(BaseModel):
    """Information about an F1 event (race weekend or testing)."""

    round_number: int | None = Field(None, description="Round number in the championship")
    event_name: str = Field(..., description="Name of the event (e.g., 'Italian Grand Prix')")
    country: str = Field(..., description="Country where the event takes place")
    location: str = Field(..., description="City/location of the circuit")
    official_event_name: str | None = Field(None, description="Full official event name")
    event_date: str | None = Field(None, description="Main event date")
    event_format: str | None = Field(
        None, description="Event format (conventional, sprint, testing)"
    )

    # Session times
    session_1_date: str | None = Field(None, description="Session 1 date and time")
    session_2_date: str | None = Field(None, description="Session 2 date and time")
    session_3_date: str | None = Field(None, description="Session 3 date and time")
    session_4_date: str | None = Field(None, description="Session 4 date and time")
    session_5_date: str | None = Field(None, description="Session 5 date and time")

    # Session names
    session_1_name: str | None = Field(None, description="Session 1 name")
    session_2_name: str | None = Field(None, description="Session 2 name")
    session_3_name: str | None = Field(None, description="Session 3 name")
    session_4_name: str | None = Field(None, description="Session 4 name")
    session_5_name: str | None = Field(None, description="Session 5 name")

    # Testing event indicator
    is_testing: bool = Field(default=False, description="Whether this is a testing event")


class ScheduleResponse(BaseModel):
    """Response containing F1 schedule information."""

    year: int = Field(..., description="Season year")
    total_events: int = Field(..., description="Total number of events")
    include_testing: bool = Field(..., description="Whether testing events are included")
    events: list[EventInfo] = Field(default_factory=list, description="List of events")

    # Optional filters applied
    round_filter: int | None = Field(None, description="Round number filter (if applied)")
    event_name_filter: str | None = Field(None, description="Event name filter (if applied)")
    only_remaining: bool = Field(
        default=False, description="Whether only remaining events are shown"
    )
    pagination: PageMeta | None = Field(None, description="Pagination metadata")

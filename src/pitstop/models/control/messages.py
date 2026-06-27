from pydantic import BaseModel, Field


class RaceControlMessage(BaseModel):
    """Single race control message."""

    time: str | None = Field(None, description="When the message was issued")
    category: str | None = Field(
        None, description="Message category (e.g., Flag, SafetyCar, CarEvent)"
    )
    message: str | None = Field(None, description="The actual message text")
    status: str | None = Field(None, description="Current session/track status")
    flag: str | None = Field(None, description="Flag status (GREEN, YELLOW, RED, etc.)")
    scope: str | None = Field(None, description="Scope of the message (Track, Sector, Driver)")
    sector: float | None = Field(None, description="Relevant sector (if applicable)")
    racing_number: str | None = Field(None, description="Driver number (if applicable)")


class RaceControlMessagesResponse(BaseModel):
    """Race control messages response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    messages: list[RaceControlMessage] = Field(description="Race control messages")
    total_messages: int = Field(description="Total number of messages")

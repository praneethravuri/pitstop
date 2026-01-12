from pydantic import BaseModel, Field
from typing import Optional


class RaceControlMessage(BaseModel):
    """Single race control message."""

    time: Optional[str] = Field(None, description="When the message was issued")
    category: Optional[str] = Field(None, description="Message category (e.g., Flag, SafetyCar, CarEvent)")
    message: Optional[str] = Field(None, description="The actual message text")
    status: Optional[str] = Field(None, description="Current session/track status")
    flag: Optional[str] = Field(None, description="Flag status (GREEN, YELLOW, RED, etc.)")
    scope: Optional[str] = Field(None, description="Scope of the message (Track, Sector, Driver)")
    sector: Optional[float] = Field(None, description="Relevant sector (if applicable)")
    racing_number: Optional[str] = Field(None, description="Driver number (if applicable)")


class RaceControlMessagesResponse(BaseModel):
    """Race control messages response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    messages: list[RaceControlMessage] = Field(description="Race control messages")
    total_messages: int = Field(description="Total number of messages")

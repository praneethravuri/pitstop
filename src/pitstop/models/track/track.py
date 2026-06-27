from pydantic import BaseModel, Field


class CornerInfo(BaseModel):
    """Information about a corner on the circuit."""

    number: int = Field(..., description="Corner number")
    letter: str | None = Field(None, description="Corner letter (if applicable)")
    distance: float | None = Field(None, description="Distance from start line in meters")
    x: float | None = Field(None, description="X coordinate")
    y: float | None = Field(None, description="Y coordinate")


class CircuitDetails(BaseModel):
    """Detailed circuit information."""

    circuit_key: int | None = Field(None, description="Circuit key/ID")
    circuit_name: str | None = Field(None, description="Circuit name")
    location: str | None = Field(None, description="Circuit location")
    country: str | None = Field(None, description="Country")
    rotation: float | None = Field(None, description="Circuit rotation angle")
    corners: list[CornerInfo] | None = Field(None, description="List of corners on the circuit")


class TrackStatusInfo(BaseModel):
    """Track status information during a session."""

    time: str = Field(..., description="Time of status")
    status: str = Field(
        ..., description="Track status code (1=Green, 2=Yellow, 4=SC, 5=Red, 6=VSC, 7=VSC Ending)"
    )
    message: str | None = Field(None, description="Human-readable status message")


class CircuitDataResponse(BaseModel):
    """Response containing circuit and track information."""

    year: int = Field(..., description="Season year")
    event_name: str = Field(..., description="Event name")
    session_name: str | None = Field(None, description="Session name (if session-specific)")

    # Circuit details
    circuit_details: CircuitDetails | None = Field(
        None, description="Circuit layout and corner information"
    )

    # Track status (session-specific)
    track_status: list[TrackStatusInfo] | None = Field(
        None, description="Track status changes during session"
    )

    # Metadata
    data_type: str = Field(..., description="Type: 'circuit_info' or 'track_status'")

from pydantic import BaseModel, Field
from typing import Optional


class CornerInfo(BaseModel):
    """Information about a corner on the circuit."""

    number: int = Field(..., description="Corner number")
    letter: Optional[str] = Field(None, description="Corner letter (if applicable)")
    distance: Optional[float] = Field(None, description="Distance from start line in meters")
    x: Optional[float] = Field(None, description="X coordinate")
    y: Optional[float] = Field(None, description="Y coordinate")


class CircuitDetails(BaseModel):
    """Detailed circuit information."""

    circuit_key: Optional[int] = Field(None, description="Circuit key/ID")
    circuit_name: Optional[str] = Field(None, description="Circuit name")
    location: Optional[str] = Field(None, description="Circuit location")
    country: Optional[str] = Field(None, description="Country")
    rotation: Optional[float] = Field(None, description="Circuit rotation angle")
    corners: Optional[list[CornerInfo]] = Field(None, description="List of corners on the circuit")


class TrackStatusInfo(BaseModel):
    """Track status information during a session."""

    time: str = Field(..., description="Time of status")
    status: str = Field(..., description="Track status code (1=Green, 2=Yellow, 4=SC, 5=Red, 6=VSC, 7=VSC Ending)")
    message: Optional[str] = Field(None, description="Human-readable status message")


class CircuitDataResponse(BaseModel):
    """Response containing circuit and track information."""

    year: int = Field(..., description="Season year")
    event_name: str = Field(..., description="Event name")
    session_name: Optional[str] = Field(None, description="Session name (if session-specific)")

    # Circuit details
    circuit_details: Optional[CircuitDetails] = Field(None, description="Circuit layout and corner information")

    # Track status (session-specific)
    track_status: Optional[list[TrackStatusInfo]] = Field(None, description="Track status changes during session")

    # Metadata
    data_type: str = Field(..., description="Type: 'circuit_info' or 'track_status'")

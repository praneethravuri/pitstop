from pydantic import BaseModel, Field
from typing import Optional


class SessionResult(BaseModel):
    """Individual driver result in a session."""

    position: Optional[float] = Field(None, description="Final position/classification")
    driver_number: str = Field(description="Driver's racing number")
    broadcast_name: str = Field(description="Driver name for broadcast")
    abbreviation: str = Field(description="3-letter driver code")
    driver_id: Optional[str] = Field(None, description="Unique driver identifier")
    team_name: str = Field(description="Constructor/team name")
    team_color: Optional[str] = Field(None, description="Team color hex code")
    first_name: Optional[str] = Field(None, description="Driver first name")
    last_name: Optional[str] = Field(None, description="Driver last name")
    full_name: Optional[str] = Field(None, description="Driver full name")
    time: Optional[str] = Field(None, description="Session time or gap")
    status: Optional[str] = Field(None, description="Finishing status")
    points: Optional[float] = Field(None, description="Points earned (for race)")
    grid_position: Optional[float] = Field(None, description="Starting grid position")
    position_gained: Optional[float] = Field(None, description="Positions gained/lost")


class SessionResultsResponse(BaseModel):
    """Session results/classification response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    results: list[SessionResult] = Field(description="List of driver results")
    total_drivers: int = Field(description="Total number of drivers")

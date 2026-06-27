from pydantic import BaseModel, Field


class SessionResult(BaseModel):
    """Individual driver result in a session."""

    position: float | None = Field(None, description="Final position/classification")
    driver_number: str = Field(description="Driver's racing number")
    broadcast_name: str = Field(description="Driver name for broadcast")
    abbreviation: str = Field(description="3-letter driver code")
    driver_id: str | None = Field(None, description="Unique driver identifier")
    team_name: str = Field(description="Constructor/team name")
    team_color: str | None = Field(None, description="Team color hex code")
    first_name: str | None = Field(None, description="Driver first name")
    last_name: str | None = Field(None, description="Driver last name")
    full_name: str | None = Field(None, description="Driver full name")
    time: str | None = Field(None, description="Session time or gap")
    status: str | None = Field(None, description="Finishing status")
    points: float | None = Field(None, description="Points earned (for race)")
    grid_position: float | None = Field(None, description="Starting grid position")
    position_gained: float | None = Field(None, description="Positions gained/lost")


class SessionResultsResponse(BaseModel):
    """Session results/classification response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    results: list[SessionResult] = Field(description="List of driver results")
    total_drivers: int = Field(description="Total number of drivers")

from pydantic import BaseModel, Field


class SessionDriversResponse(BaseModel):
    """Session drivers response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    year: int = Field(description="Season year")
    drivers: list[str] = Field(description="List of driver abbreviations")
    total_drivers: int = Field(description="Total number of drivers")

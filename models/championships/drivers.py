from pydantic import BaseModel, Field


class DriverStanding(BaseModel):
    """Individual driver standing entry."""

    position: int = Field(..., description="Championship position")
    driver_name: str = Field(..., description="Full name of the driver")
    driver_code: str = Field(..., description="Three-letter driver code")
    team: str = Field(..., description="Team/Constructor name")
    points: float = Field(..., description="Championship points")
    wins: int = Field(..., description="Number of race wins")


class DriverStandingsResponse(BaseModel):
    """Complete driver standings for a season."""

    year: int = Field(..., description="Season year")
    standings: list[DriverStanding] = Field(
        ..., description="List of driver standings"
    )

from pydantic import BaseModel, Field


class TireStint(BaseModel):
    """Tire data for a single lap."""

    driver: str = Field(description="Driver abbreviation")
    lap_number: int = Field(description="Lap number")
    compound: str | None = Field(
        None, description="Tire compound (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)"
    )
    tyre_life: float | None = Field(None, description="Age of tire in laps")
    fresh_tyre: bool | None = Field(None, description="Whether it's a new tire")


class TireStrategyResponse(BaseModel):
    """Tire strategy response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver: str | None = Field(None, description="Driver filter (if applied)")
    tire_data: list[TireStint] = Field(description="Tire data per lap")
    total_laps: int = Field(description="Total number of laps")

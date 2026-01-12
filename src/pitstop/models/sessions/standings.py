from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class DriverStanding(BaseModel):
    """Individual driver championship standing."""

    position: int = Field(description="Championship position")
    position_text: str = Field(description="Position as text (may include tie indicators)")
    points: float = Field(description="Total championship points")
    wins: int = Field(description="Number of race wins")
    driver_id: str = Field(description="Unique driver identifier")
    driver_number: int = Field(description="Driver racing number")
    driver_code: str = Field(description="3-letter driver code")
    given_name: str = Field(description="Driver first name")
    family_name: str = Field(description="Driver last name")
    date_of_birth: Optional[date] = Field(None, description="Driver date of birth")
    nationality: str = Field(description="Driver nationality")
    constructor_ids: list[str] = Field(description="Constructor IDs driver raced for")
    constructor_names: list[str] = Field(description="Constructor names driver raced for")
    constructor_nationalities: list[str] = Field(description="Constructor nationalities")


class ConstructorStanding(BaseModel):
    """Individual constructor championship standing."""

    position: int = Field(description="Championship position")
    position_text: str = Field(description="Position as text (may include tie indicators)")
    points: float = Field(description="Total championship points")
    wins: int = Field(description="Number of race wins")
    constructor_id: str = Field(description="Unique constructor identifier")
    constructor_name: str = Field(description="Constructor/team name")
    nationality: str = Field(description="Constructor nationality")


class StandingsResponse(BaseModel):
    """Championship standings response."""

    year: int = Field(description="Season year")
    round: Optional[int] = Field(None, description="Round number (None for final/current standings)")
    round_name: Optional[str] = Field(None, description="Grand Prix name if round specified")
    drivers: Optional[list[DriverStanding]] = Field(None, description="Driver standings")
    constructors: Optional[list[ConstructorStanding]] = Field(None, description="Constructor standings")

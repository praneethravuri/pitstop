from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class DriverInfo(BaseModel):
    """Information about an F1 driver."""

    driver_id: str = Field(..., description="Unique driver identifier")
    driver_number: Optional[int] = Field(None, description="Driver's racing number")
    driver_code: Optional[str] = Field(None, description="Three-letter driver code (e.g., 'VER', 'HAM')")
    given_name: str = Field(..., description="Driver's first name")
    family_name: str = Field(..., description="Driver's last name")
    date_of_birth: Optional[date] = Field(None, description="Driver's date of birth")
    nationality: str = Field(..., description="Driver's nationality")
    team_name: Optional[str] = Field(None, description="Current team (for specific season)")
    team_color: Optional[str] = Field(None, description="Team color hex code")


class ConstructorInfo(BaseModel):
    """Information about an F1 constructor/team."""

    constructor_id: str = Field(..., description="Unique constructor identifier")
    constructor_name: str = Field(..., description="Constructor/team name")
    nationality: str = Field(..., description="Constructor's nationality")
    team_color: Optional[str] = Field(None, description="Team color hex code")
    drivers: Optional[list[str]] = Field(None, description="Driver names in the team (for specific season)")


class CornerInfo(BaseModel):
    """Information about a corner on the circuit."""

    number: int = Field(..., description="Corner number")
    letter: Optional[str] = Field(None, description="Corner letter (if applicable)")
    distance: Optional[float] = Field(None, description="Distance from start line in meters")
    x: Optional[float] = Field(None, description="X coordinate")
    y: Optional[float] = Field(None, description="Y coordinate")


class CircuitInfo(BaseModel):
    """Information about an F1 circuit."""

    circuit_id: str = Field(..., description="Unique circuit identifier")
    circuit_name: str = Field(..., description="Circuit name")
    location: str = Field(..., description="City/location of the circuit")
    country: str = Field(..., description="Country where the circuit is located")
    lat: Optional[float] = Field(None, description="Latitude coordinate")
    lng: Optional[float] = Field(None, description="Longitude coordinate")
    url: Optional[str] = Field(None, description="Wikipedia or official URL")
    rotation: Optional[float] = Field(None, description="Circuit rotation angle")
    corners: Optional[list[CornerInfo]] = Field(None, description="List of corners on the circuit")


class TireCompoundInfo(BaseModel):
    """Information about tire compounds."""

    compound_name: str = Field(..., description="Compound name (SOFT, MEDIUM, HARD, etc.)")
    color: Optional[str] = Field(None, description="Display color for the compound")
    description: Optional[str] = Field(None, description="Compound description")


class ReferenceDataResponse(BaseModel):
    """Response containing reference/metadata information."""

    reference_type: str = Field(..., description="Type: 'driver', 'constructor', 'circuit', 'tire_compounds'")
    year: Optional[int] = Field(None, description="Season year (if applicable)")

    # Optional data based on type
    drivers: Optional[list[DriverInfo]] = Field(None, description="Driver information")
    constructors: Optional[list[ConstructorInfo]] = Field(None, description="Constructor information")
    circuits: Optional[list[CircuitInfo]] = Field(None, description="Circuit information")
    tire_compounds: Optional[list[TireCompoundInfo]] = Field(None, description="Tire compound information")

    # Metadata
    total_records: int = Field(..., description="Total number of records returned")
    name_filter: Optional[str] = Field(None, description="Name filter applied (if any)")

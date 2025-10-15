from pydantic import BaseModel, Field
from typing import Optional


class FastestLapData(BaseModel):
    """Data for fastest lap(s) in a session."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    team: Optional[str] = Field(None, description="Team name")
    lap_time: Optional[str] = Field(None, description="Lap time")
    lap_number: int = Field(..., description="Lap number when fastest lap was set")
    compound: Optional[str] = Field(None, description="Tire compound used")
    tyre_life: Optional[float] = Field(None, description="Tire age in laps")


class SectorData(BaseModel):
    """Sector times data for a driver."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    lap_number: int = Field(..., description="Lap number")
    sector_1_time: Optional[str] = Field(None, description="Sector 1 time")
    sector_2_time: Optional[str] = Field(None, description="Sector 2 time")
    sector_3_time: Optional[str] = Field(None, description="Sector 3 time")
    lap_time: Optional[str] = Field(None, description="Total lap time")
    is_personal_best: Optional[bool] = Field(None, description="Whether this is a personal best lap")


class PitStopData(BaseModel):
    """Pit stop information."""

    driver: str = Field(..., description="Driver abbreviation")
    driver_number: str = Field(..., description="Driver number")
    lap_number: int = Field(..., description="Lap number of pit stop")
    pit_in_time: Optional[str] = Field(None, description="Time when entering pit lane")
    pit_out_time: Optional[str] = Field(None, description="Time when exiting pit lane")
    pit_duration: Optional[str] = Field(None, description="Duration of pit stop")
    compound_before: Optional[str] = Field(None, description="Tire compound before stop")
    compound_after: Optional[str] = Field(None, description="Tire compound after stop")


class AdvancedSessionDataResponse(BaseModel):
    """Response containing advanced session data."""

    session_name: str = Field(..., description="Session name (e.g., 'Race', 'Qualifying')")
    event_name: str = Field(..., description="Event name (e.g., 'Italian Grand Prix')")
    year: int = Field(..., description="Season year")
    data_type: str = Field(..., description="Type of data: 'fastest_laps', 'sector_times', 'pit_stops'")

    # Optional data based on type
    fastest_laps: Optional[list[FastestLapData]] = Field(None, description="Fastest lap data")
    sector_times: Optional[list[SectorData]] = Field(None, description="Sector times data")
    pit_stops: Optional[list[PitStopData]] = Field(None, description="Pit stop data")

    # Metadata
    total_records: int = Field(..., description="Total number of records returned")
    driver_filter: Optional[str] = Field(None, description="Driver filter applied (if any)")

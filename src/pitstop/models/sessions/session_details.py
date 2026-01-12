from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SessionInfo(BaseModel):
    """Basic information about a session."""

    name: str = Field(description="Session name (e.g., 'Free Practice 1', 'Qualifying', 'Race')")
    session_type: str = Field(description="Session type identifier (FP1, FP2, FP3, Q, S, R)")
    event_name: str = Field(description="Grand Prix name")
    location: str = Field(description="Circuit location")
    country: str = Field(description="Country")
    circuit_name: str = Field(description="Official circuit name")
    year: int = Field(description="Season year")
    round: int = Field(description="Round number in the season")
    session_date: Optional[datetime] = Field(None, description="Session start date and time")


class DriverSessionResult(BaseModel):
    """Individual driver result in a session."""

    position: Optional[int] = Field(None, description="Final position")
    driver_number: str = Field(description="Driver number")
    driver_name: str = Field(description="Full driver name")
    abbreviation: str = Field(description="3-letter driver abbreviation")
    team: str = Field(description="Team name")
    time: Optional[str] = Field(None, description="Session time (for race/qualifying)")
    gap_to_leader: Optional[str] = Field(None, description="Gap to session leader")
    laps_completed: Optional[int] = Field(None, description="Number of laps completed")
    points: Optional[float] = Field(None, description="Points earned (for race)")
    status: Optional[str] = Field(None, description="Finishing status")


class SessionWeather(BaseModel):
    """Weather information for the session."""

    air_temp: Optional[float] = Field(None, description="Air temperature (°C)")
    track_temp: Optional[float] = Field(None, description="Track temperature (°C)")
    humidity: Optional[float] = Field(None, description="Humidity percentage")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")
    rainfall: Optional[bool] = Field(None, description="Whether it rained during session")


class LapInfo(BaseModel):
    """Information about the fastest lap."""

    driver: str = Field(description="Driver who set the lap")
    lap_time: str = Field(description="Lap time")
    lap_number: int = Field(description="Lap number")
    compound: Optional[str] = Field(None, description="Tire compound used")


class SessionDetailsResponse(BaseModel):
    """Complete session details response."""

    session_info: SessionInfo = Field(description="Basic session information")
    results: list[DriverSessionResult] = Field(description="Driver results/classification")
    weather: Optional[SessionWeather] = Field(None, description="Weather conditions")
    fastest_lap: Optional[LapInfo] = Field(None, description="Fastest lap of the session")
    total_laps: Optional[int] = Field(None, description="Total laps in session")
    session_duration: Optional[str] = Field(None, description="Session duration")

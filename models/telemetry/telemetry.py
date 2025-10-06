from pydantic import BaseModel, Field
from typing import Optional


class TelemetryPoint(BaseModel):
    """Single telemetry data point."""

    session_time: Optional[str] = Field(None, description="Session time")
    distance: Optional[float] = Field(None, description="Distance in meters")
    speed: Optional[float] = Field(None, description="Speed in km/h")
    rpm: Optional[float] = Field(None, description="Engine RPM")
    n_gear: Optional[int] = Field(None, description="Current gear (1-8)")
    throttle: Optional[float] = Field(None, description="Throttle position (0-100%)")
    brake: Optional[float] = Field(None, description="Brake application (0-100% or boolean)")
    drs: Optional[int] = Field(None, description="DRS status")
    x: Optional[float] = Field(None, description="X position coordinate")
    y: Optional[float] = Field(None, description="Y position coordinate")
    z: Optional[float] = Field(None, description="Z position coordinate")


class LapTelemetryResponse(BaseModel):
    """Lap telemetry response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver: str = Field(description="Driver abbreviation")
    lap_number: int = Field(description="Lap number")
    lap_time: Optional[str] = Field(None, description="Lap time")
    telemetry: list[TelemetryPoint] = Field(description="Telemetry data points")
    total_points: int = Field(description="Total number of telemetry points")


class TelemetryComparisonResponse(BaseModel):
    """Telemetry comparison response for two drivers."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    driver1: str = Field(description="First driver abbreviation")
    driver1_lap: int = Field(description="First driver lap number")
    driver1_telemetry: list[TelemetryPoint] = Field(description="First driver telemetry")
    driver1_lap_time: Optional[str] = Field(None, description="First driver lap time")
    driver2: str = Field(description="Second driver abbreviation")
    driver2_lap: int = Field(description="Second driver lap number")
    driver2_telemetry: list[TelemetryPoint] = Field(description="Second driver telemetry")
    driver2_lap_time: Optional[str] = Field(None, description="Second driver lap time")

from pydantic import BaseModel, Field
from typing import Optional


class WeatherDataPoint(BaseModel):
    """Single weather data point."""

    time: Optional[str] = Field(None, description="Timestamp")
    air_temp: Optional[float] = Field(None, description="Air temperature (°C)")
    track_temp: Optional[float] = Field(None, description="Track surface temperature (°C)")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    pressure: Optional[float] = Field(None, description="Atmospheric pressure (mbar)")
    wind_speed: Optional[float] = Field(None, description="Wind speed (m/s)")
    wind_direction: Optional[float] = Field(None, description="Wind direction (degrees)")
    rainfall: Optional[bool] = Field(None, description="Whether it's raining")


class SessionWeatherDataResponse(BaseModel):
    """Session weather data response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    weather_data: list[WeatherDataPoint] = Field(description="Weather data points throughout session")
    total_points: int = Field(description="Total number of weather data points")

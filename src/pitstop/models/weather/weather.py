from pydantic import BaseModel, Field


class WeatherDataPoint(BaseModel):
    """Single weather data point."""

    time: str | None = Field(None, description="Timestamp")
    air_temp: float | None = Field(None, description="Air temperature (°C)")
    track_temp: float | None = Field(None, description="Track surface temperature (°C)")
    humidity: float | None = Field(None, description="Relative humidity (%)")
    pressure: float | None = Field(None, description="Atmospheric pressure (mbar)")
    wind_speed: float | None = Field(None, description="Wind speed (m/s)")
    wind_direction: float | None = Field(None, description="Wind direction (degrees)")
    rainfall: bool | None = Field(None, description="Whether it's raining")


class SessionWeatherDataResponse(BaseModel):
    """Session weather data response."""

    session_name: str = Field(description="Session name")
    event_name: str = Field(description="Grand Prix name")
    weather_data: list[WeatherDataPoint] = Field(
        description="Weather data points throughout session"
    )
    total_points: int = Field(description="Total number of weather data points")

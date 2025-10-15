"""Pydantic models for weather forecast responses."""

from pydantic import BaseModel, Field
from typing import Optional


class WeatherForecast(BaseModel):
    """Weather forecast data point."""
    datetime: str = Field(..., description="Forecast datetime (ISO 8601)")
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    pressure: int = Field(..., description="Atmospheric pressure in hPa")
    weather_main: str = Field(..., description="Weather condition (e.g., 'Rain', 'Clear')")
    weather_description: str = Field(..., description="Weather description")
    clouds: int = Field(..., description="Cloudiness percentage")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_deg: Optional[int] = Field(None, description="Wind direction in degrees")
    rain_3h: Optional[float] = Field(None, description="Rain volume for last 3 hours in mm")
    pop: Optional[float] = Field(None, description="Probability of precipitation (0-1)")


class WeatherForecastResponse(BaseModel):
    """Response for weather forecast."""
    circuit: str = Field(..., description="Circuit name")
    city: str = Field(..., description="City name")
    country: str = Field(..., description="Country code")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    forecasts: list[WeatherForecast] = Field(..., description="List of forecast data points")
    total_forecasts: int = Field(..., description="Total number of forecasts")

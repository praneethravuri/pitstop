"""
Weather API Client - Forecasting for F1 race weekends

Uses OpenWeatherMap API for weather forecasting.
Free tier: 1000 calls/day, 60 calls/minute
API Documentation: https://openweathermap.org/api

Set environment variable: OPENWEATHER_API_KEY
Get free key at: https://openweathermap.org/appid
"""

import httpx
import os
from typing import Optional, Any
from datetime import datetime


class WeatherClient:
    """Client for weather forecasting APIs."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    # Circuit coordinates (lat, lon) for major F1 tracks
    CIRCUIT_COORDS = {
        "Monaco": (43.7347, 7.4206),
        "Silverstone": (52.0786, -1.0169),
        "Monza": (45.6156, 9.2811),
        "Spa": (50.4372, 5.9714),
        "Suzuka": (34.8431, 136.5408),
        "Singapore": (1.2914, 103.8640),
        "Austin": (30.1328, -97.6411),
        "Interlagos": (-23.7036, -46.6997),
        "Bahrain": (26.0325, 50.5106),
        "Jeddah": (21.6319, 39.1044),
        "Melbourne": (-37.8497, 144.9680),
        "Shanghai": (31.3389, 121.2197),
        "Imola": (44.3439, 11.7167),
        "Miami": (25.9581, -80.2389),
        "Barcelona": (41.57, 2.2611),
        "Red Bull Ring": (47.2197, 14.7647),
        "Hungaroring": (47.5789, 19.2486),
        "Zandvoort": (52.3889, 4.5408),
        "Baku": (40.3725, 49.8533),
        "Mexico City": (19.4042, -99.0907),
        "Las Vegas": (36.1147, -115.1728),
        "Abu Dhabi": (24.4672, 54.6031),
        "Montreal": (45.5047, -73.5272),
    }

    def __init__(self, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialize Weather client.

        Args:
            api_key: OpenWeatherMap API key (or set OPENWEATHER_API_KEY env var)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenWeatherMap API key required. Set OPENWEATHER_API_KEY environment variable "
                "or pass api_key parameter. Get free key at https://openweathermap.org/appid"
            )
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)

    def _get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> dict:
        """
        Make GET request to OpenWeatherMap API.

        Args:
            endpoint: API endpoint (e.g., '/forecast')
            params: Query parameters

        Returns:
            Dictionary containing response data
        """
        url = f"{self.BASE_URL}{endpoint}"
        params = params or {}
        params['appid'] = self.api_key
        params['units'] = 'metric'  # Use metric units

        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_coordinates(self, circuit_name: str) -> Optional[tuple[float, float]]:
        """
        Get circuit coordinates.

        Args:
            circuit_name: Circuit name (e.g., "Monaco", "Silverstone")

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        return self.CIRCUIT_COORDS.get(circuit_name)

    def get_5day_forecast(
        self,
        circuit_name: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> dict:
        """
        Get 5-day weather forecast (3-hour intervals).

        Args:
            circuit_name: Circuit name for coordinate lookup
            lat: Optional latitude override
            lon: Optional longitude override

        Returns:
            Forecast data with list of 3-hour forecasts
        """
        if lat is None or lon is None:
            coords = self.get_coordinates(circuit_name)
            if not coords:
                raise ValueError(f"Unknown circuit: {circuit_name}. Provide lat/lon manually.")
            lat, lon = coords

        params = {
            'lat': lat,
            'lon': lon
        }

        return self._get('/forecast', params)

    def get_current_weather(
        self,
        circuit_name: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None
    ) -> dict:
        """
        Get current weather conditions.

        Args:
            circuit_name: Circuit name for coordinate lookup
            lat: Optional latitude override
            lon: Optional longitude override

        Returns:
            Current weather data
        """
        if lat is None or lon is None:
            coords = self.get_coordinates(circuit_name)
            if not coords:
                raise ValueError(f"Unknown circuit: {circuit_name}. Provide lat/lon manually.")
            lat, lon = coords

        params = {
            'lat': lat,
            'lon': lon
        }

        return self._get('/weather', params)

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    # Example usage (requires OPENWEATHER_API_KEY env var)
    try:
        client = WeatherClient()

        # Get 5-day forecast for Monaco
        forecast = client.get_5day_forecast("Monaco")
        print(f"5-day forecast for Monaco")
        print(f"City: {forecast['city']['name']}")
        print(f"Total forecasts: {forecast['cnt']}")

        # Get current weather
        current = client.get_current_weather("Monaco")
        print(f"\nCurrent weather: {current['weather'][0]['description']}")
        print(f"Temperature: {current['main']['temp']}°C")
        print(f"Humidity: {current['main']['humidity']}%")

        client.close()
    except ValueError as e:
        print(f"Error: {e}")
        print("Set OPENWEATHER_API_KEY environment variable to test")

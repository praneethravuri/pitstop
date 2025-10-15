from clients.weather_client import WeatherClient
from typing import Optional
from models.forecast import WeatherForecastResponse, WeatherForecast
from datetime import datetime

# Note: Weather client requires OPENWEATHER_API_KEY environment variable
# Initialize on first use to avoid errors if key not set


def get_race_weather_forecast(
    circuit: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> WeatherForecastResponse:
    """
    Get 5-day weather forecast for race weekend at circuit location.

    Provides 3-hour interval forecasts including temperature, rain probability,
    wind speed, and weather conditions.

    Args:
        circuit: Circuit name (e.g., "Monaco", "Silverstone", "Monza")
        latitude: Optional latitude override
        longitude: Optional longitude override

    Returns:
        WeatherForecastResponse with 5-day forecast data

    Example:
        get_race_weather_forecast("Monaco") → 5-day forecast for Monaco
        get_race_weather_forecast("Custom", 43.7, 7.4) → Custom location

    Note:
        Requires OPENWEATHER_API_KEY environment variable.
        Get free key at https://openweathermap.org/appid
    """
    try:
        client = WeatherClient()
    except ValueError as e:
        # Return empty response if API key not configured
        return WeatherForecastResponse(
            circuit=circuit,
            city="N/A",
            country="N/A",
            latitude=latitude or 0.0,
            longitude=longitude or 0.0,
            forecasts=[],
            total_forecasts=0
        )

    try:
        # Get forecast data
        forecast_data = client.get_5day_forecast(circuit, latitude, longitude)

        # Extract location info
        city = forecast_data['city']['name']
        country = forecast_data['city']['country']
        lat = forecast_data['city']['coord']['lat']
        lon = forecast_data['city']['coord']['lon']

        # Convert forecast list to Pydantic models
        forecasts = []
        for item in forecast_data['list']:
            forecast = WeatherForecast(
                datetime=datetime.fromtimestamp(item['dt']).isoformat(),
                temperature=item['main']['temp'],
                feels_like=item['main']['feels_like'],
                humidity=item['main']['humidity'],
                pressure=item['main']['pressure'],
                weather_main=item['weather'][0]['main'],
                weather_description=item['weather'][0]['description'],
                clouds=item['clouds']['all'],
                wind_speed=item['wind']['speed'],
                wind_deg=item['wind'].get('deg'),
                rain_3h=item.get('rain', {}).get('3h'),
                pop=item.get('pop')
            )
            forecasts.append(forecast)

        return WeatherForecastResponse(
            circuit=circuit,
            city=city,
            country=country,
            latitude=lat,
            longitude=lon,
            forecasts=forecasts,
            total_forecasts=len(forecasts)
        )

    finally:
        client.close()


if __name__ == "__main__":
    # Test with Monaco
    print("Testing get_race_weather_forecast with Monaco...")
    result = get_race_weather_forecast("Monaco")
    print(f"Circuit: {result.circuit}")
    print(f"Location: {result.city}, {result.country}")
    print(f"Total forecasts: {result.total_forecasts}")
    if result.forecasts:
        first = result.forecasts[0]
        print(f"\nFirst forecast:")
        print(f"  Time: {first.datetime}")
        print(f"  Temp: {first.temperature}°C")
        print(f"  Conditions: {first.weather_description}")
        if first.rain_3h:
            print(f"  Rain: {first.rain_3h}mm")

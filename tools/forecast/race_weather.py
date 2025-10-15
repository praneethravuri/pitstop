from clients.weather_client import WeatherClient
from typing import Optional
from models.forecast import WeatherForecastResponse, WeatherForecast
from datetime import datetime, timedelta

# Note: Weather client requires OPENWEATHER_API_KEY environment variable
# Initialize on first use to avoid errors if key not set


def get_session_forecast(
    circuit: str,
    session_datetime: str,
    hours_before: int = 3,
    hours_after: int = 3,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> WeatherForecastResponse:
    """
    Get hourly weather forecast for specific session time window.

    Filters 5-day forecast to show only forecasts around session time.

    Args:
        circuit: Circuit name (e.g., "Monaco", "Silverstone")
        session_datetime: Session start time (ISO 8601 format, e.g., "2024-05-26T15:00:00")
        hours_before: Hours before session to include (default: 3)
        hours_after: Hours after session to include (default: 3)
        latitude: Optional latitude override
        longitude: Optional longitude override

    Returns:
        WeatherForecastResponse with filtered forecasts around session time

    Example:
        get_session_forecast("Monaco", "2024-05-26T15:00:00") → Race session forecast
        get_session_forecast("Monaco", "2024-05-25T14:00:00", 2, 2) → Qualifying forecast
    """
    try:
        client = WeatherClient()
    except ValueError:
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
        # Parse session datetime
        session_dt = datetime.fromisoformat(session_datetime.replace('Z', '+00:00'))

        # Calculate time window
        start_window = session_dt - timedelta(hours=hours_before)
        end_window = session_dt + timedelta(hours=hours_after)

        # Get full 5-day forecast
        forecast_data = client.get_5day_forecast(circuit, latitude, longitude)

        # Extract location info
        city = forecast_data['city']['name']
        country = forecast_data['city']['country']
        lat = forecast_data['city']['coord']['lat']
        lon = forecast_data['city']['coord']['lon']

        # Filter forecasts to session window
        forecasts = []
        for item in forecast_data['list']:
            forecast_dt = datetime.fromtimestamp(item['dt'])

            # Only include if within window
            if start_window <= forecast_dt <= end_window:
                forecast = WeatherForecast(
                    datetime=forecast_dt.isoformat(),
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


def get_rain_probability(
    circuit: str,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> WeatherForecastResponse:
    """
    Get rain probability timeline for race weekend.

    Filters forecast to show only rain-related predictions with probability.

    Args:
        circuit: Circuit name (e.g., "Monaco", "Silverstone")
        start_datetime: Optional start time (ISO 8601 format)
        end_datetime: Optional end time (ISO 8601 format)
        latitude: Optional latitude override
        longitude: Optional longitude override

    Returns:
        WeatherForecastResponse with rain probability data

    Example:
        get_rain_probability("Monaco") → All rain forecasts for next 5 days
        get_rain_probability("Monaco", "2024-05-26T10:00:00", "2024-05-26T18:00:00") → Race day rain
    """
    try:
        client = WeatherClient()
    except ValueError:
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
        # Get full 5-day forecast
        forecast_data = client.get_5day_forecast(circuit, latitude, longitude)

        # Extract location info
        city = forecast_data['city']['name']
        country = forecast_data['city']['country']
        lat = forecast_data['city']['coord']['lat']
        lon = forecast_data['city']['coord']['lon']

        # Parse time window if provided
        start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00')) if start_datetime else None
        end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00')) if end_datetime else None

        # Filter for rain probability
        forecasts = []
        for item in forecast_data['list']:
            forecast_dt = datetime.fromtimestamp(item['dt'])

            # Check time window
            if start_dt and forecast_dt < start_dt:
                continue
            if end_dt and forecast_dt > end_dt:
                continue

            # Include if rain probability exists or rain detected
            pop = item.get('pop', 0)
            rain = item.get('rain', {}).get('3h', 0)
            weather_main = item['weather'][0]['main']

            if pop > 0 or rain > 0 or weather_main in ['Rain', 'Drizzle', 'Thunderstorm']:
                forecast = WeatherForecast(
                    datetime=forecast_dt.isoformat(),
                    temperature=item['main']['temp'],
                    feels_like=item['main']['feels_like'],
                    humidity=item['main']['humidity'],
                    pressure=item['main']['pressure'],
                    weather_main=weather_main,
                    weather_description=item['weather'][0]['description'],
                    clouds=item['clouds']['all'],
                    wind_speed=item['wind']['speed'],
                    wind_deg=item['wind'].get('deg'),
                    rain_3h=rain if rain > 0 else None,
                    pop=pop
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

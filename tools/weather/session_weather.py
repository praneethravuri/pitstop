from clients.fastf1_client import FastF1Client
from typing import Union
from models.weather import SessionWeatherDataResponse, WeatherDataPoint
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_weather(year: int, gp: Union[str, int], session: str) -> SessionWeatherDataResponse:
    """
    Get time-series weather data - temp, humidity, pressure, wind, rainfall.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        SessionWeatherDataResponse with weather points

    Example:
        get_session_weather(2024, "Spa", "R") → Weather throughout race
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=True, messages=False)

    event = session_obj.event
    weather_df = session_obj.weather_data

    # Convert to Pydantic models
    weather_points = []
    for idx, row in weather_df.iterrows():
        point = WeatherDataPoint(
            time=str(row['Time']) if pd.notna(row.get('Time')) else None,
            air_temp=float(row['AirTemp']) if pd.notna(row.get('AirTemp')) else None,
            track_temp=float(row['TrackTemp']) if pd.notna(row.get('TrackTemp')) else None,
            humidity=float(row['Humidity']) if pd.notna(row.get('Humidity')) else None,
            pressure=float(row['Pressure']) if pd.notna(row.get('Pressure')) else None,
            wind_speed=float(row['WindSpeed']) if pd.notna(row.get('WindSpeed')) else None,
            wind_direction=float(row['WindDirection']) if pd.notna(row.get('WindDirection')) else None,
            rainfall=bool(row['Rainfall']) if pd.notna(row.get('Rainfall')) else None,
        )
        weather_points.append(point)

    return SessionWeatherDataResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        weather_data=weather_points,
        total_points=len(weather_points)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco Grand Prix Race
    print("Testing get_session_weather with 2024 Monaco GP Race...")
    weather = get_session_weather(2024, "Monaco", "R")
    print(f"\nSession: {weather.session_name}")
    print(f"Weather data points: {weather.total_points}")

    if weather.weather_data:
        # Calculate summary from weather data
        air_temps = [w.air_temp for w in weather.weather_data if w.air_temp is not None]
        track_temps = [w.track_temp for w in weather.weather_data if w.track_temp is not None]
        humidities = [w.humidity for w in weather.weather_data if w.humidity is not None]

        if air_temps:
            print(f"\nWeather summary:")
            print(f"  Air Temp range: {min(air_temps):.1f}°C - {max(air_temps):.1f}°C")
        if track_temps:
            print(f"  Track Temp range: {min(track_temps):.1f}°C - {max(track_temps):.1f}°C")
        if humidities:
            print(f"  Humidity: {sum(humidities)/len(humidities):.1f}%")

    # Test JSON serialization
    print(f"\nJSON: {weather.model_dump_json()[:100]}...")

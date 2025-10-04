from clients.fastf1_client import FastF1Client
from typing import Union

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_weather(year: int, gp: Union[str, int], session: str):
    """
    Get weather data throughout a session.

    Retrieves time-series weather information recorded during a session, including
    temperature, humidity, pressure, wind, and rainfall data. Essential for
    understanding session conditions and their impact on performance.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        pandas.DataFrame: Weather data throughout the session with columns:
        - Time: Session timestamp
        - AirTemp: Air temperature (°C)
        - TrackTemp: Track surface temperature (°C)
        - Humidity: Relative humidity (%)
        - Pressure: Atmospheric pressure (mbar)
        - WindSpeed: Wind speed (m/s)
        - WindDirection: Wind direction (degrees)
        - Rainfall: Whether it's raining (boolean)

    Examples:
        >>> # Get weather data from 2024 Spa race
        >>> weather = get_session_weather(2024, "Spa", "R")

        >>> # Check weather conditions during qualifying
        >>> quali_weather = get_session_weather(2024, "Silverstone", "Q")

        >>> # Analyze weather changes during practice
        >>> fp1_weather = get_session_weather(2024, "Monaco", "FP1")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=True, messages=False)
    return session_obj.weather_data

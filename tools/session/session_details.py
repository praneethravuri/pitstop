from clients.fastf1_client import FastF1Client
from models import SessionDetailsResponse, SessionInfo, DriverSessionResult, SessionWeather, LapInfo
from datetime import datetime
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_details(
    year: int,
    gp: str | int,
    session: str,
    include_weather: bool = True,
    include_fastest_lap: bool = True
) -> SessionDetailsResponse:
    """
    Get comprehensive details of a specific F1 session.

    Provides complete session information including results, weather conditions,
    fastest lap, and session statistics for any F1 session from 2018 onwards.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1' (Free Practice 1), 'FP2' (Free Practice 2),
                'FP3' (Free Practice 3), 'Q' (Qualifying), 'S' (Sprint), 'R' (Race)
        include_weather: Whether to include weather data (default: True)
        include_fastest_lap: Whether to include fastest lap information (default: True)

    Returns:
        SessionDetailsResponse: Complete session details including:
        - Session information (name, location, date, circuit)
        - Driver results/classification with positions, times, and teams
        - Weather conditions (temperature, humidity, wind, rainfall)
        - Fastest lap information (driver, time, compound)
        - Session statistics (total laps, duration)

    Examples:
        >>> # Get Free Practice 1 details from 2019 Monza GP
        >>> get_session_details(2019, "Monza", "FP1")

        >>> # Get Race results from 2024 Monaco GP
        >>> get_session_details(2024, "Monaco", "R")

        >>> # Get Qualifying results without weather data
        >>> get_session_details(2023, "Silverstone", "Q", include_weather=False)
    """
    # Load session
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(
        laps=include_fastest_lap,
        telemetry=False,
        weather=include_weather,
        messages=False
    )

    # Extract event info
    event = session_obj.event

    # Build session info
    session_info = SessionInfo(
        name=session_obj.name,
        session_type=session.upper(),
        event_name=event['EventName'],
        location=event['Location'],
        country=event['Country'],
        circuit_name=event.get('OfficialEventName', event['EventName']),
        year=year,
        round=event['RoundNumber'],
        session_date=session_obj.date if hasattr(session_obj, 'date') else None
    )

    # Extract driver results
    results_df = session_obj.results
    driver_results = []

    for idx, row in results_df.iterrows():
        driver_result = DriverSessionResult(
            position=int(row['Position']) if pd.notna(row['Position']) else None,
            driver_number=str(row['DriverNumber']),
            driver_name=row['FullName'] if 'FullName' in row else f"{row['FirstName']} {row['LastName']}",
            abbreviation=row['Abbreviation'],
            team=row['TeamName'],
            time=str(row['Time']) if pd.notna(row.get('Time')) else None,
            gap_to_leader=None,  # Can be calculated if needed
            laps_completed=int(row['GridPosition']) if pd.notna(row.get('GridPosition')) else None,
            points=float(row['Points']) if pd.notna(row.get('Points')) else None,
            status=row.get('Status', None)
        )
        driver_results.append(driver_result)

    # Extract weather data
    weather = None
    if include_weather and hasattr(session_obj, 'weather_data') and session_obj.weather_data is not None:
        weather_df = session_obj.weather_data
        if not weather_df.empty:
            # Get average or latest weather data
            latest_weather = weather_df.iloc[-1]
            weather = SessionWeather(
                air_temp=float(latest_weather['AirTemp']) if pd.notna(latest_weather.get('AirTemp')) else None,
                track_temp=float(latest_weather['TrackTemp']) if pd.notna(latest_weather.get('TrackTemp')) else None,
                humidity=float(latest_weather['Humidity']) if pd.notna(latest_weather.get('Humidity')) else None,
                pressure=float(latest_weather['Pressure']) if pd.notna(latest_weather.get('Pressure')) else None,
                wind_speed=float(latest_weather['WindSpeed']) if pd.notna(latest_weather.get('WindSpeed')) else None,
                rainfall=bool(latest_weather['Rainfall']) if pd.notna(latest_weather.get('Rainfall')) else None
            )

    # Extract fastest lap
    fastest_lap = None
    if include_fastest_lap and hasattr(session_obj, 'laps') and session_obj.laps is not None:
        fastest = session_obj.laps.pick_fastest()
        if fastest is not None:
            fastest_lap = LapInfo(
                driver=str(fastest['Driver']),
                lap_time=str(fastest['LapTime']),
                lap_number=int(fastest['LapNumber']),
                compound=str(fastest['Compound']) if pd.notna(fastest.get('Compound')) else None
            )

    # Calculate total laps
    total_laps = None
    if hasattr(session_obj, 'laps') and session_obj.laps is not None:
        total_laps = len(session_obj.laps)

    # Session duration
    session_duration = None
    if hasattr(session_obj, 'session_start_time') and hasattr(session_obj, 'session_end_time'):
        if session_obj.session_start_time and session_obj.session_end_time:
            duration = session_obj.session_end_time - session_obj.session_start_time
            session_duration = str(duration)

    return SessionDetailsResponse(
        session_info=session_info,
        results=driver_results,
        weather=weather,
        fastest_lap=fastest_lap,
        total_laps=total_laps,
        session_duration=session_duration
    )


if __name__ == "__main__":
    # Test with 2024 Monaco Grand Prix Race
    print("Testing get_session_details...")

    print("\n1. Getting session details for 2024 Monaco GP Race:")
    details = get_session_details(2024, "Monaco", "R")
    print(f"   Session: {details.session_info.name}")
    print(f"   Location: {details.session_info.location}, {details.session_info.country}")
    print(f"   Date: {details.session_info.session_date}")
    print(f"   Total laps: {details.total_laps}")

    if details.results:
        print(f"\n   Top 3 finishers:")
        for i in range(min(3, len(details.results))):
            result = details.results[i]
            print(f"   {result.position}. {result.driver_name} ({result.team}) - {result.time}")

    if details.fastest_lap:
        print(f"\n   Fastest lap: {details.fastest_lap.driver} - {details.fastest_lap.lap_time}")

    if details.weather:
        print(f"\n   Weather: {details.weather.air_temp}°C, Humidity: {details.weather.humidity}%")

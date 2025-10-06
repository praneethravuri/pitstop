from clients.fastf1_client import FastF1Client
from typing import Union, Optional
from models.telemetry import TelemetryComparisonResponse, TelemetryPoint
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def _telemetry_to_points(telemetry_df):
    """Convert telemetry DataFrame to list of TelemetryPoint pydantic models."""
    points = []
    for idx, row in telemetry_df.iterrows():
        point = TelemetryPoint(
            session_time=str(row['SessionTime']) if pd.notna(row.get('SessionTime')) else None,
            distance=float(row['Distance']) if pd.notna(row.get('Distance')) else None,
            speed=float(row['Speed']) if pd.notna(row.get('Speed')) else None,
            rpm=float(row['RPM']) if pd.notna(row.get('RPM')) else None,
            n_gear=int(row['nGear']) if pd.notna(row.get('nGear')) else None,
            throttle=float(row['Throttle']) if pd.notna(row.get('Throttle')) else None,
            brake=float(row['Brake']) if pd.notna(row.get('Brake')) else None,
            drs=int(row['DRS']) if pd.notna(row.get('DRS')) else None,
            x=float(row['X']) if pd.notna(row.get('X')) else None,
            y=float(row['Y']) if pd.notna(row.get('Y')) else None,
            z=float(row['Z']) if pd.notna(row.get('Z')) else None,
        )
        points.append(point)
    return points


def compare_driver_telemetry(
    year: int,
    gp: Union[str, int],
    session: str,
    driver1: Union[str, int],
    driver2: Union[str, int],
    lap1: Optional[int] = None,
    lap2: Optional[int] = None
) -> TelemetryComparisonResponse:
    """
    Compare telemetry data between two drivers.

    Retrieves and returns telemetry data for two drivers side-by-side, enabling
    detailed performance comparison. Useful for analyzing racing lines, braking
    points, and overall driving style differences.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver1: First driver identifier (3-letter code or number)
        driver2: Second driver identifier (3-letter code or number)
        lap1: Lap number for driver1 (uses fastest lap if None)
        lap2: Lap number for driver2 (uses fastest lap if None)

    Returns:
        TelemetryComparisonResponse: Telemetry data for both drivers in JSON-serializable format

    Examples:
        >>> # Compare fastest laps between Verstappen and Hamilton
        >>> comparison = compare_driver_telemetry(2024, "Monza", "Q", "VER", "HAM")

        >>> # Compare specific laps
        >>> comparison = compare_driver_telemetry(2024, "Monza", "R", "VER", "HAM", lap1=15, lap2=15)
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=True, weather=False, messages=False)

    event = session_obj.event

    # Get driver 1 lap
    driver1_laps = session_obj.laps.pick_drivers(driver1)
    if lap1 is None:
        lap1_data = driver1_laps.pick_fastest()
    else:
        lap1_data = driver1_laps[driver1_laps['LapNumber'] == lap1].iloc[0]

    # Get driver 2 lap
    driver2_laps = session_obj.laps.pick_drivers(driver2)
    if lap2 is None:
        lap2_data = driver2_laps.pick_fastest()
    else:
        lap2_data = driver2_laps[driver2_laps['LapNumber'] == lap2].iloc[0]

    # Get telemetry
    tel1_df = lap1_data.get_telemetry()
    tel2_df = lap2_data.get_telemetry()

    # Convert to Pydantic models
    driver1_telemetry = _telemetry_to_points(tel1_df)
    driver2_telemetry = _telemetry_to_points(tel2_df)

    return TelemetryComparisonResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        driver1=str(lap1_data['Driver']),
        driver1_lap=int(lap1_data['LapNumber']),
        driver1_telemetry=driver1_telemetry,
        driver1_lap_time=str(lap1_data['LapTime']) if pd.notna(lap1_data.get('LapTime')) else None,
        driver2=str(lap2_data['Driver']),
        driver2_lap=int(lap2_data['LapNumber']),
        driver2_telemetry=driver2_telemetry,
        driver2_lap_time=str(lap2_data['LapTime']) if pd.notna(lap2_data.get('LapTime')) else None,
    )


if __name__ == "__main__":
    # Test with 2024 Monza Grand Prix Qualifying
    print("Testing compare_driver_telemetry...")

    # Compare Verstappen and Hamilton's fastest laps
    print("\n1. Comparing VER vs HAM fastest laps in 2024 Monza Qualifying:")
    comparison = compare_driver_telemetry(2024, "Monza", "Q", "VER", "HAM")
    print(f"   Session: {comparison.session_name}")
    print(f"   {comparison.driver1} lap {comparison.driver1_lap}: {comparison.driver1_lap_time} ({len(comparison.driver1_telemetry)} points)")
    print(f"   {comparison.driver2} lap {comparison.driver2_lap}: {comparison.driver2_lap_time} ({len(comparison.driver2_telemetry)} points)")

    # Test JSON serialization
    print(f"\n   JSON: {comparison.model_dump_json()[:100]}...")

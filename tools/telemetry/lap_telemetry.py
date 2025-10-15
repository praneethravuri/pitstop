from clients.fastf1_client import FastF1Client
from typing import Union
from models.telemetry import LapTelemetryResponse, TelemetryPoint
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_lap_telemetry(year: int, gp: Union[str, int], session: str, driver: Union[str, int], lap_number: int) -> LapTelemetryResponse:
    """
    Get high-frequency telemetry for a lap - speed, throttle, brake, gear, RPM, DRS.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Driver code or number
        lap_number: Specific lap number

    Returns:
        LapTelemetryResponse with telemetry points

    Example:
        get_lap_telemetry(2024, "Monza", "R", "VER", 15) → VER lap 15 telemetry
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=True, weather=False, messages=False)

    event = session_obj.event

    driver_laps = session_obj.laps.pick_drivers(driver)
    lap = driver_laps[driver_laps['LapNumber'] == lap_number].iloc[0]
    telemetry_df = lap.get_telemetry()

    # Convert to Pydantic models
    telemetry_points = []
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
        telemetry_points.append(point)

    return LapTelemetryResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        driver=str(lap['Driver']),
        lap_number=lap_number,
        lap_time=str(lap['LapTime']) if pd.notna(lap.get('LapTime')) else None,
        telemetry=telemetry_points,
        total_points=len(telemetry_points)
    )


if __name__ == "__main__":
    # Test with 2024 Monza Grand Prix Qualifying
    print("Testing get_lap_telemetry...")

    # First, find Verstappen's fastest lap number
    from tools.session.laps import get_laps
    print("\n1. Finding Verstappen's fastest lap in 2024 Monza Qualifying...")
    fastest_lap = get_laps(2024, "Monza", "Q", driver="VER", lap_type="fastest")
    lap_num = fastest_lap.lap_data.lap_number
    print(f"   Fastest lap is lap {lap_num}: {fastest_lap.lap_data.lap_time}")

    # Get telemetry for that lap
    print(f"\n2. Getting telemetry for lap {lap_num}...")
    telemetry = get_lap_telemetry(2024, "Monza", "Q", "VER", lap_num)
    print(f"   Telemetry data points: {telemetry.total_points}")
    if telemetry.telemetry:
        print(f"   Sample speed: {telemetry.telemetry[0].speed} km/h")

    # Test JSON serialization
    print(f"\n   JSON: {telemetry.model_dump_json()[:100]}...")

from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.sessions import LapsResponse, FastestLapResponse, LapData
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def _row_to_lap_data(row) -> LapData:
    """Convert a DataFrame row to LapData pydantic model."""
    return LapData(
        time=str(row['Time']) if pd.notna(row.get('Time')) else None,
        driver=str(row['Driver']) if pd.notna(row.get('Driver')) else "",
        driver_number=str(row['DriverNumber']) if pd.notna(row.get('DriverNumber')) else "",
        lap_time=str(row['LapTime']) if pd.notna(row.get('LapTime')) else None,
        lap_number=int(row['LapNumber']) if pd.notna(row.get('LapNumber')) else 0,
        stint=int(row['Stint']) if pd.notna(row.get('Stint')) else None,
        pit_out_time=str(row['PitOutTime']) if pd.notna(row.get('PitOutTime')) else None,
        pit_in_time=str(row['PitInTime']) if pd.notna(row.get('PitInTime')) else None,
        sector_1_time=str(row['Sector1Time']) if pd.notna(row.get('Sector1Time')) else None,
        sector_2_time=str(row['Sector2Time']) if pd.notna(row.get('Sector2Time')) else None,
        sector_3_time=str(row['Sector3Time']) if pd.notna(row.get('Sector3Time')) else None,
        sector_1_session_time=str(row['Sector1SessionTime']) if pd.notna(row.get('Sector1SessionTime')) else None,
        sector_2_session_time=str(row['Sector2SessionTime']) if pd.notna(row.get('Sector2SessionTime')) else None,
        sector_3_session_time=str(row['Sector3SessionTime']) if pd.notna(row.get('Sector3SessionTime')) else None,
        speed_i1=float(row['SpeedI1']) if pd.notna(row.get('SpeedI1')) else None,
        speed_i2=float(row['SpeedI2']) if pd.notna(row.get('SpeedI2')) else None,
        speed_fl=float(row['SpeedFL']) if pd.notna(row.get('SpeedFL')) else None,
        speed_st=float(row['SpeedST']) if pd.notna(row.get('SpeedST')) else None,
        is_personal_best=bool(row['IsPersonalBest']) if pd.notna(row.get('IsPersonalBest')) else None,
        compound=str(row['Compound']) if pd.notna(row.get('Compound')) else None,
        tyre_life=float(row['TyreLife']) if pd.notna(row.get('TyreLife')) else None,
        fresh_tyre=bool(row['FreshTyre']) if pd.notna(row.get('FreshTyre')) else None,
        team=str(row['Team']) if pd.notna(row.get('Team')) else None,
        lap_start_time=str(row['LapStartTime']) if pd.notna(row.get('LapStartTime')) else None,
        lap_start_date=str(row['LapStartDate']) if pd.notna(row.get('LapStartDate')) else None,
        track_status=str(row['TrackStatus']) if pd.notna(row.get('TrackStatus')) else None,
        position=float(row['Position']) if pd.notna(row.get('Position')) else None,
        deleted=bool(row['Deleted']) if pd.notna(row.get('Deleted')) else None,
        deleted_reason=str(row['DeletedReason']) if pd.notna(row.get('DeletedReason')) else None,
        fast_f1_generated=bool(row['FastF1Generated']) if pd.notna(row.get('FastF1Generated')) else None,
        is_accurate=bool(row['IsAccurate']) if pd.notna(row.get('IsAccurate')) else None,
    )


def get_laps(
    year: int,
    gp: Union[str, int],
    session: str,
    driver: Optional[Union[str, int]] = None,
    lap_type: Optional[Literal["all", "fastest"]] = "all"
) -> Union[LapsResponse, FastestLapResponse]:
    """
    Get lap data - all laps, driver-specific, or fastest laps with times and sectors.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        driver: Driver code/number (optional, all if None)
        lap_type: 'all' or 'fastest' (default: 'all')

    Returns:
        LapsResponse or FastestLapResponse with lap times, sectors, compounds

    Examples:
        get_laps(2024, "Monza", "R") → All laps from race
        get_laps(2024, "Monaco", "Q", lap_type="fastest") → Fastest overall lap
    """
    # Load session with lap data
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    event = session_obj.event

    # Get laps based on driver filter
    if driver:
        laps = session_obj.laps.pick_drivers(driver)
    else:
        laps = session_obj.laps

    # Return based on lap_type
    if lap_type == "fastest":
        fastest_lap = laps.pick_fastest()
        lap_data = _row_to_lap_data(fastest_lap)

        return FastestLapResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            driver=str(fastest_lap['Driver']),
            lap_data=lap_data
        )
    else:
        laps_list = []
        for idx, row in laps.iterrows():
            laps_list.append(_row_to_lap_data(row))

        return LapsResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            driver=str(driver) if driver else None,
            lap_type=lap_type,
            laps=laps_list,
            total_laps=len(laps_list)
        )


if __name__ == "__main__":
    # Test with 2024 Monza Grand Prix Race
    print("Testing get_laps with different scenarios...")

    # Test 1: Get all laps for a specific driver
    print("\n1. Getting all laps for Verstappen in 2024 Monza Race:")
    ver_laps = get_laps(2024, "Monza", "R", driver="VER")
    print(f"   Session: {ver_laps.session_name}")
    print(f"   Total laps: {ver_laps.total_laps}")
    if ver_laps.laps:
        print(f"   First lap time: {ver_laps.laps[0].lap_time}")

    # Test 2: Get fastest lap overall
    print("\n2. Getting fastest lap in 2024 Monza Qualifying:")
    fastest = get_laps(2024, "Monza", "Q", lap_type="fastest")
    print(f"   Fastest lap by {fastest.driver}: {fastest.lap_data.lap_time}")

    # Test JSON serialization
    print(f"\n   JSON: {fastest.model_dump_json()[:100]}...")

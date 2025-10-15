from clients.fastf1_client import FastF1Client
from typing import Union
from models.sessions import LapsResponse, LapData
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


def get_qualifying_sessions(
    year: int,
    gp: Union[str, int],
    segment: str = "all"
) -> dict[str, LapsResponse]:
    """
    Split qualifying into Q1, Q2, Q3 segments with lap data for each.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        segment: 'Q1', 'Q2', 'Q3', or 'all' (default: 'all' returns all segments)

    Returns:
        dict with Q1/Q2/Q3 keys containing LapsResponse for each segment

    Example:
        get_qualifying_sessions(2024, "Monaco") → All Q1/Q2/Q3 segments
        get_qualifying_sessions(2024, "Monaco", "Q3") → Q3 only
    """
    session_obj = fastf1_client.get_session(year, gp, 'Q')
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    event = session_obj.event
    laps = session_obj.laps

    # Split qualifying into segments
    q1_laps, q2_laps, q3_laps = laps.split_qualifying_sessions()

    results = {}

    # Convert each segment to LapsResponse
    if segment in ["all", "Q1"] and q1_laps is not None and len(q1_laps) > 0:
        q1_list = [_row_to_lap_data(row) for idx, row in q1_laps.iterrows()]
        results["Q1"] = LapsResponse(
            session_name="Q1",
            event_name=event['EventName'],
            driver=None,
            lap_type="all",
            laps=q1_list,
            total_laps=len(q1_list)
        )

    if segment in ["all", "Q2"] and q2_laps is not None and len(q2_laps) > 0:
        q2_list = [_row_to_lap_data(row) for idx, row in q2_laps.iterrows()]
        results["Q2"] = LapsResponse(
            session_name="Q2",
            event_name=event['EventName'],
            driver=None,
            lap_type="all",
            laps=q2_list,
            total_laps=len(q2_list)
        )

    if segment in ["all", "Q3"] and q3_laps is not None and len(q3_laps) > 0:
        q3_list = [_row_to_lap_data(row) for idx, row in q3_laps.iterrows()]
        results["Q3"] = LapsResponse(
            session_name="Q3",
            event_name=event['EventName'],
            driver=None,
            lap_type="all",
            laps=q3_list,
            total_laps=len(q3_list)
        )

    return results


if __name__ == "__main__":
    # Test with 2024 Monaco Grand Prix
    print("Testing get_qualifying_sessions with 2024 Monaco GP...")

    # Get all sessions
    sessions = get_qualifying_sessions(2024, "Monaco")
    print(f"\nTotal segments: {len(sessions)}")

    for segment, data in sessions.items():
        print(f"\n{segment}:")
        print(f"  Total laps: {data.total_laps}")
        if data.laps:
            print(f"  Drivers: {len(set(lap.driver for lap in data.laps))}")

    # Get Q3 only
    q3_only = get_qualifying_sessions(2024, "Monaco", "Q3")
    print(f"\nQ3 only: {q3_only['Q3'].total_laps} laps")

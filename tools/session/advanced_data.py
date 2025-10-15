from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.sessions.advanced_data import (
    AdvancedSessionDataResponse,
    FastestLapData,
    SectorData,
    PitStopData,
)
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_advanced_session_data(
    year: int,
    gp: Union[str, int],
    session: str,
    data_type: Literal["fastest_laps", "sector_times", "pit_stops"],
    driver: Optional[Union[str, int]] = None,
    top_n: Optional[int] = None,
) -> AdvancedSessionDataResponse:
    """
    Get advanced session data including fastest laps, sector times, and pit stops.

    A comprehensive tool that provides deep session analysis data. Use this single tool
    for all advanced session data queries instead of multiple separate tools.

    Use this tool to:
    - Get fastest lap times for all drivers or specific driver
    - Analyze sector times to see where drivers gain/lose time
    - Track pit stops including timing, duration, and tire changes
    - Compare performance across different parts of the track

    Args:
        year: The season year (2018 onwards for detailed data)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1' (Free Practice 1), 'FP2', 'FP3',
                'Q' (Qualifying), 'S' (Sprint), 'R' (Race)
        data_type: Type of data to retrieve:
                  - 'fastest_laps': Get fastest lap times per driver
                  - 'sector_times': Get sector time breakdowns
                  - 'pit_stops': Get pit stop data with timing and tire changes
        driver: Optional - Driver identifier as 3-letter code (e.g., 'VER', 'HAM')
                or number (e.g., 1, 44). If None, returns data for all drivers.
        top_n: Optional - Limit results to top N (useful for fastest_laps)

    Returns:
        AdvancedSessionDataResponse: Advanced session data in JSON-serializable format.

    Examples:
        >>> # Get fastest lap for each driver in Monaco qualifying
        >>> fastest = get_advanced_session_data(2024, "Monaco", "Q", "fastest_laps")

        >>> # Get Verstappen's fastest lap in the race
        >>> ver_fastest = get_advanced_session_data(2024, "Monza", "R", "fastest_laps", driver="VER")

        >>> # Get top 3 fastest laps from qualifying
        >>> top_3 = get_advanced_session_data(2024, "Monaco", "Q", "fastest_laps", top_n=3)

        >>> # Get sector times for all drivers
        >>> sectors = get_advanced_session_data(2024, "Monza", "Q", "sector_times")

        >>> # Get Hamilton's sector times
        >>> ham_sectors = get_advanced_session_data(2024, "Monza", "Q", "sector_times", driver="HAM")

        >>> # Get all pit stops from the race
        >>> pit_stops = get_advanced_session_data(2024, "Monza", "R", "pit_stops")

        >>> # Get Leclerc's pit stops
        >>> lec_pits = get_advanced_session_data(2024, "Monza", "R", "pit_stops", driver="LEC")
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

    if data_type == "fastest_laps":
        # Get fastest lap per driver
        if driver:
            # Single driver fastest lap
            fastest_lap = laps.pick_fastest()
            fastest_laps_list = [
                FastestLapData(
                    driver=str(fastest_lap['Driver']),
                    driver_number=str(fastest_lap['DriverNumber']),
                    team=str(fastest_lap['Team']) if pd.notna(fastest_lap.get('Team')) else None,
                    lap_time=str(fastest_lap['LapTime']) if pd.notna(fastest_lap.get('LapTime')) else None,
                    lap_number=int(fastest_lap['LapNumber']),
                    compound=str(fastest_lap['Compound']) if pd.notna(fastest_lap.get('Compound')) else None,
                    tyre_life=float(fastest_lap['TyreLife']) if pd.notna(fastest_lap.get('TyreLife')) else None,
                )
            ]
        else:
            # Fastest lap for each driver
            drivers_list = laps['Driver'].unique()
            fastest_laps_list = []

            for drv in drivers_list:
                try:
                    driver_laps = laps.pick_drivers(drv)
                    if len(driver_laps) > 0:
                        fastest_lap = driver_laps.pick_fastest()
                        fastest_laps_list.append(
                            FastestLapData(
                                driver=str(fastest_lap['Driver']),
                                driver_number=str(fastest_lap['DriverNumber']),
                                team=str(fastest_lap['Team']) if pd.notna(fastest_lap.get('Team')) else None,
                                lap_time=str(fastest_lap['LapTime']) if pd.notna(fastest_lap.get('LapTime')) else None,
                                lap_number=int(fastest_lap['LapNumber']),
                                compound=str(fastest_lap['Compound']) if pd.notna(fastest_lap.get('Compound')) else None,
                                tyre_life=float(fastest_lap['TyreLife']) if pd.notna(fastest_lap.get('TyreLife')) else None,
                            )
                        )
                except Exception:
                    continue

            # Sort by lap time and limit to top_n if specified
            fastest_laps_list.sort(key=lambda x: x.lap_time if x.lap_time else '99:99:99.999')
            if top_n:
                fastest_laps_list = fastest_laps_list[:top_n]

        return AdvancedSessionDataResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            data_type=data_type,
            fastest_laps=fastest_laps_list,
            total_records=len(fastest_laps_list),
            driver_filter=str(driver) if driver else None,
        )

    elif data_type == "sector_times":
        # Get sector times data
        sector_times_list = []

        for idx, row in laps.iterrows():
            if pd.notna(row.get('Sector1Time')) or pd.notna(row.get('Sector2Time')) or pd.notna(row.get('Sector3Time')):
                sector_times_list.append(
                    SectorData(
                        driver=str(row['Driver']),
                        driver_number=str(row['DriverNumber']),
                        lap_number=int(row['LapNumber']),
                        sector_1_time=str(row['Sector1Time']) if pd.notna(row.get('Sector1Time')) else None,
                        sector_2_time=str(row['Sector2Time']) if pd.notna(row.get('Sector2Time')) else None,
                        sector_3_time=str(row['Sector3Time']) if pd.notna(row.get('Sector3Time')) else None,
                        lap_time=str(row['LapTime']) if pd.notna(row.get('LapTime')) else None,
                        is_personal_best=bool(row['IsPersonalBest']) if pd.notna(row.get('IsPersonalBest')) else None,
                    )
                )

        # Limit to top_n if specified
        if top_n:
            sector_times_list = sector_times_list[:top_n]

        return AdvancedSessionDataResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            data_type=data_type,
            sector_times=sector_times_list,
            total_records=len(sector_times_list),
            driver_filter=str(driver) if driver else None,
        )

    elif data_type == "pit_stops":
        # Get pit stop data - laps where pit in/out times exist
        pit_stops_list = []

        for idx, row in laps.iterrows():
            # A pit stop occurs when there's a PitInTime or PitOutTime
            if pd.notna(row.get('PitInTime')) or pd.notna(row.get('PitOutTime')):
                # Try to calculate pit duration
                pit_duration = None
                if pd.notna(row.get('PitInTime')) and pd.notna(row.get('PitOutTime')):
                    try:
                        pit_in = pd.Timedelta(row['PitInTime'])
                        pit_out = pd.Timedelta(row['PitOutTime'])
                        duration = pit_out - pit_in
                        pit_duration = str(duration)
                    except Exception:
                        pass

                # Get compound before and after (if available from adjacent laps)
                compound_before = None
                compound_after = str(row['Compound']) if pd.notna(row.get('Compound')) else None

                # Try to get previous lap's compound
                try:
                    prev_laps = laps[
                        (laps['Driver'] == row['Driver']) &
                        (laps['LapNumber'] < row['LapNumber'])
                    ]
                    if len(prev_laps) > 0:
                        prev_lap = prev_laps.iloc[-1]
                        compound_before = str(prev_lap['Compound']) if pd.notna(prev_lap.get('Compound')) else None
                except Exception:
                    pass

                pit_stops_list.append(
                    PitStopData(
                        driver=str(row['Driver']),
                        driver_number=str(row['DriverNumber']),
                        lap_number=int(row['LapNumber']),
                        pit_in_time=str(row['PitInTime']) if pd.notna(row.get('PitInTime')) else None,
                        pit_out_time=str(row['PitOutTime']) if pd.notna(row.get('PitOutTime')) else None,
                        pit_duration=pit_duration,
                        compound_before=compound_before,
                        compound_after=compound_after,
                    )
                )

        # Limit to top_n if specified
        if top_n:
            pit_stops_list = pit_stops_list[:top_n]

        return AdvancedSessionDataResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            data_type=data_type,
            pit_stops=pit_stops_list,
            total_records=len(pit_stops_list),
            driver_filter=str(driver) if driver else None,
        )


if __name__ == "__main__":
    # Test advanced session data functionality
    print("Testing get_advanced_session_data...")

    # Test 1: Get fastest laps
    print("\n1. Getting fastest laps from 2024 Monaco Qualifying:")
    fastest = get_advanced_session_data(2024, "Monaco", "Q", "fastest_laps", top_n=5)
    print(f"   Top 5 fastest laps:")
    if fastest.fastest_laps:
        for i, lap in enumerate(fastest.fastest_laps[:5], 1):
            print(f"   {i}. {lap.driver} - {lap.lap_time} (Lap {lap.lap_number})")

    # Test 2: Get pit stops
    print("\n2. Getting pit stops from 2024 Monza Race:")
    pit_stops = get_advanced_session_data(2024, "Monza", "R", "pit_stops", driver="VER")
    print(f"   Total pit stops for VER: {pit_stops.total_records}")
    if pit_stops.pit_stops:
        for stop in pit_stops.pit_stops[:3]:
            print(f"   Lap {stop.lap_number}: {stop.compound_before} → {stop.compound_after}")

    # Test 3: Get sector times
    print("\n3. Getting sector times for Leclerc in 2024 Monaco Q:")
    sectors = get_advanced_session_data(2024, "Monaco", "Q", "sector_times", driver="LEC", top_n=3)
    print(f"   Total laps with sector data: {sectors.total_records}")

    # Test JSON serialization
    print(f"\n   JSON: {fastest.model_dump_json()[:150]}...")

from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.analysis import (
    AnalysisResponse,
    RacePaceData,
    TireDegradationData,
    StintSummary,
    ConsistencyData,
)
import pandas as pd
import numpy as np

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_analysis(
    year: int,
    gp: Union[str, int],
    session: str,
    analysis_type: Literal["race_pace", "tire_degradation", "stint_summary", "consistency"],
    driver: Optional[Union[str, int]] = None,
) -> AnalysisResponse:
    """
    Advanced race analysis - pace, tire degradation, stint summaries, consistency metrics.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        analysis_type: 'race_pace', 'tire_degradation', 'stint_summary', 'consistency'
        driver: Driver code/number (optional, all drivers if None)

    Returns:
        AnalysisResponse with pace data, degradation, stints, or consistency stats

    Examples:
        get_analysis(2024, "Monaco", "R", "race_pace") → Pace analysis for all drivers
        get_analysis(2024, "Monza", "R", "tire_degradation", driver="VER") → VER's tire wear
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

    if analysis_type == "race_pace":
        # Calculate race pace (excluding pit laps and inaccurate laps)
        race_pace_list = []

        if driver:
            drivers_to_analyze = [driver]
        else:
            drivers_to_analyze = laps['Driver'].unique()

        for drv in drivers_to_analyze:
            try:
                driver_laps = laps.pick_drivers(drv)

                # Filter for clean laps: no pit stops, accurate timing, not deleted
                clean_laps = driver_laps[
                    (pd.isna(driver_laps['PitInTime'])) &
                    (pd.isna(driver_laps['PitOutTime'])) &
                    (driver_laps['IsAccurate'] == True) &
                    (driver_laps['Deleted'] == False)
                ]

                if len(clean_laps) > 0:
                    # Convert lap times to seconds for calculation
                    lap_times_seconds = clean_laps['LapTime'].dt.total_seconds()

                    avg_time = lap_times_seconds.mean()
                    median_time = lap_times_seconds.median()
                    fastest_time = lap_times_seconds.min()

                    race_pace_list.append(
                        RacePaceData(
                            driver=str(clean_laps.iloc[0]['Driver']),
                            driver_number=str(clean_laps.iloc[0]['DriverNumber']),
                            average_lap_time=str(pd.Timedelta(seconds=avg_time)),
                            median_lap_time=str(pd.Timedelta(seconds=median_time)),
                            fastest_lap_time=str(pd.Timedelta(seconds=fastest_time)),
                            total_laps=len(driver_laps),
                            clean_laps=len(clean_laps),
                        )
                    )
            except Exception:
                continue

        return AnalysisResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            analysis_type=analysis_type,
            race_pace=race_pace_list,
            total_records=len(race_pace_list),
            driver_filter=str(driver) if driver else None,
        )

    elif analysis_type == "tire_degradation":
        # Analyze tire degradation per stint
        degradation_list = []

        if driver:
            drivers_to_analyze = [driver]
        else:
            drivers_to_analyze = laps['Driver'].unique()

        for drv in drivers_to_analyze:
            try:
                driver_laps = laps.pick_drivers(drv)

                # Group by stint
                stints = driver_laps['Stint'].unique()

                for stint in stints:
                    if pd.notna(stint):
                        stint_laps = driver_laps[driver_laps['Stint'] == stint]

                        # Filter clean laps for analysis
                        clean_stint_laps = stint_laps[
                            (pd.isna(stint_laps['PitInTime'])) &
                            (pd.isna(stint_laps['PitOutTime'])) &
                            (stint_laps['IsAccurate'] == True) &
                            (stint_laps['Deleted'] == False)
                        ]

                        if len(clean_stint_laps) >= 2:
                            first_lap = clean_stint_laps.iloc[0]
                            last_lap = clean_stint_laps.iloc[-1]

                            first_time = first_lap['LapTime'].total_seconds() if pd.notna(first_lap['LapTime']) else None
                            last_time = last_lap['LapTime'].total_seconds() if pd.notna(last_lap['LapTime']) else None

                            degradation = None
                            if first_time and last_time:
                                deg_seconds = last_time - first_time
                                degradation = str(pd.Timedelta(seconds=deg_seconds))

                            avg_time = clean_stint_laps['LapTime'].dt.total_seconds().mean()

                            degradation_list.append(
                                TireDegradationData(
                                    driver=str(first_lap['Driver']),
                                    driver_number=str(first_lap['DriverNumber']),
                                    stint=int(stint),
                                    compound=str(first_lap['Compound']) if pd.notna(first_lap.get('Compound')) else None,
                                    first_lap_time=str(first_lap['LapTime']) if pd.notna(first_lap['LapTime']) else None,
                                    last_lap_time=str(last_lap['LapTime']) if pd.notna(last_lap['LapTime']) else None,
                                    average_lap_time=str(pd.Timedelta(seconds=avg_time)),
                                    degradation=degradation,
                                    stint_length=len(clean_stint_laps),
                                )
                            )
            except Exception:
                continue

        return AnalysisResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            analysis_type=analysis_type,
            tire_degradation=degradation_list,
            total_records=len(degradation_list),
            driver_filter=str(driver) if driver else None,
        )

    elif analysis_type == "stint_summary":
        # Summarize each stint
        stint_summaries_list = []

        if driver:
            drivers_to_analyze = [driver]
        else:
            drivers_to_analyze = laps['Driver'].unique()

        for drv in drivers_to_analyze:
            try:
                driver_laps = laps.pick_drivers(drv)

                # Group by stint
                stints = driver_laps['Stint'].unique()

                for stint in stints:
                    if pd.notna(stint):
                        stint_laps = driver_laps[driver_laps['Stint'] == stint]

                        # Filter clean laps
                        clean_stint_laps = stint_laps[
                            (pd.isna(stint_laps['PitInTime'])) &
                            (pd.isna(stint_laps['PitOutTime'])) &
                            (stint_laps['IsAccurate'] == True)
                        ]

                        if len(clean_stint_laps) > 0:
                            avg_time = clean_stint_laps['LapTime'].dt.total_seconds().mean()
                            fastest_time = clean_stint_laps['LapTime'].dt.total_seconds().min()

                            stint_summaries_list.append(
                                StintSummary(
                                    driver=str(clean_stint_laps.iloc[0]['Driver']),
                                    driver_number=str(clean_stint_laps.iloc[0]['DriverNumber']),
                                    stint=int(stint),
                                    compound=str(clean_stint_laps.iloc[0]['Compound']) if pd.notna(clean_stint_laps.iloc[0].get('Compound')) else None,
                                    stint_length=len(clean_stint_laps),
                                    average_lap_time=str(pd.Timedelta(seconds=avg_time)),
                                    fastest_lap_time=str(pd.Timedelta(seconds=fastest_time)),
                                )
                            )
            except Exception:
                continue

        return AnalysisResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            analysis_type=analysis_type,
            stint_summaries=stint_summaries_list,
            total_records=len(stint_summaries_list),
            driver_filter=str(driver) if driver else None,
        )

    elif analysis_type == "consistency":
        # Analyze driver consistency
        consistency_list = []

        if driver:
            drivers_to_analyze = [driver]
        else:
            drivers_to_analyze = laps['Driver'].unique()

        for drv in drivers_to_analyze:
            try:
                driver_laps = laps.pick_drivers(drv)

                # Filter clean laps
                clean_laps = driver_laps[
                    (pd.isna(driver_laps['PitInTime'])) &
                    (pd.isna(driver_laps['PitOutTime'])) &
                    (driver_laps['IsAccurate'] == True) &
                    (driver_laps['Deleted'] == False)
                ]

                if len(clean_laps) >= 3:  # Need at least 3 laps for meaningful stats
                    lap_times_seconds = clean_laps['LapTime'].dt.total_seconds()

                    avg_time = lap_times_seconds.mean()
                    std_dev = lap_times_seconds.std()
                    coefficient_of_variation = (std_dev / avg_time) * 100 if avg_time > 0 else None

                    consistency_list.append(
                        ConsistencyData(
                            driver=str(clean_laps.iloc[0]['Driver']),
                            driver_number=str(clean_laps.iloc[0]['DriverNumber']),
                            average_lap_time=str(pd.Timedelta(seconds=avg_time)),
                            std_deviation=float(std_dev),
                            coefficient_of_variation=float(coefficient_of_variation) if coefficient_of_variation else None,
                            total_laps=len(clean_laps),
                        )
                    )
            except Exception:
                continue

        # Sort by coefficient of variation (most consistent first)
        consistency_list.sort(key=lambda x: x.coefficient_of_variation if x.coefficient_of_variation else 999)

        return AnalysisResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            year=year,
            analysis_type=analysis_type,
            consistency=consistency_list,
            total_records=len(consistency_list),
            driver_filter=str(driver) if driver else None,
        )


if __name__ == "__main__":
    # Test analysis functionality
    print("Testing get_analysis...")

    # Test 1: Race pace analysis
    print("\n1. Getting race pace for 2024 Monaco Race:")
    pace = get_analysis(2024, "Monaco", "R", "race_pace")
    print(f"   Total drivers analyzed: {pace.total_records}")
    if pace.race_pace:
        print(f"   Sample: {pace.race_pace[0].driver} - Avg: {pace.race_pace[0].average_lap_time}")

    # Test 2: Tire degradation
    print("\n2. Getting tire degradation for VER in 2024 Monza:")
    deg = get_analysis(2024, "Monza", "R", "tire_degradation", driver="VER")
    print(f"   Total stints: {deg.total_records}")
    if deg.tire_degradation:
        for stint in deg.tire_degradation:
            print(f"   Stint {stint.stint} ({stint.compound}): {stint.degradation} degradation")

    # Test 3: Consistency analysis
    print("\n3. Getting consistency for 2024 Monaco Qualifying:")
    consistency = get_analysis(2024, "Monaco", "Q", "consistency")
    print(f"   Total drivers: {consistency.total_records}")
    if consistency.consistency:
        print(f"   Most consistent: {consistency.consistency[0].driver} (CV: {consistency.consistency[0].coefficient_of_variation:.2f}%)")

    # Test JSON serialization
    print(f"\n   JSON: {pace.model_dump_json()[:150]}...")

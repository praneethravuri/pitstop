from clients.fastf1_client import FastF1Client
from typing import Union, Optional
from pydantic import BaseModel, Field
import pandas as pd


# Initialize FastF1 client
fastf1_client = FastF1Client()


class LapEvolution(BaseModel):
    """Lap time evolution data point."""
    lap_number: int = Field(..., description="Lap number")
    best_time: str = Field(..., description="Best lap time for this lap number across all drivers")
    driver: str = Field(..., description="Driver who set this time")
    driver_number: str = Field(..., description="Driver number")
    improvement_from_lap_1: Optional[float] = Field(None, description="Seconds faster than lap 1 best")


class TrackEvolutionResponse(BaseModel):
    """Response for track evolution data."""
    session_name: str = Field(..., description="Session name")
    event_name: str = Field(..., description="Event name")
    evolution: list[LapEvolution] = Field(..., description="Lap time evolution throughout session")
    total_laps: int = Field(..., description="Total number of laps analyzed")
    total_improvement: Optional[float] = Field(None, description="Total improvement in seconds from start to end")


def get_track_evolution(
    year: int,
    gp: Union[str, int],
    session: str,
    max_laps: Optional[int] = None
) -> TrackEvolutionResponse:
    """
    Track how lap times improved during session as track evolution occurred.

    Shows fastest lap per lap number to see track rubbering in and improvement.

    Args:
        year: Season year (2018+)
        gp: Grand Prix name or round
        session: 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'
        max_laps: Optional limit to first N laps

    Returns:
        TrackEvolutionResponse with lap-by-lap improvement data

    Example:
        get_track_evolution(2024, "Monaco", "FP1") → Practice track evolution
        get_track_evolution(2024, "Monaco", "Q", 20) → First 20 laps of qualifying
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=True, telemetry=False, weather=False, messages=False)

    event = session_obj.event
    laps = session_obj.laps

    # Filter for valid laps only (not deleted, not pit laps)
    valid_laps = laps[
        (laps['IsAccurate'] == True) &
        (laps['Deleted'] == False) &
        (pd.notna(laps['LapTime']))
    ].copy()

    if len(valid_laps) == 0:
        return TrackEvolutionResponse(
            session_name=session_obj.name,
            event_name=event['EventName'],
            evolution=[],
            total_laps=0,
            total_improvement=None
        )

    # Convert LapTime to seconds for comparison
    valid_laps['LapTimeSeconds'] = valid_laps['LapTime'].dt.total_seconds()

    # Group by lap number and find fastest for each lap
    evolution_data = []
    lap_numbers = sorted(valid_laps['LapNumber'].unique())

    if max_laps:
        lap_numbers = [ln for ln in lap_numbers if ln <= max_laps]

    first_lap_best = None

    for lap_num in lap_numbers:
        lap_data = valid_laps[valid_laps['LapNumber'] == lap_num]
        fastest_idx = lap_data['LapTimeSeconds'].idxmin()
        fastest_lap = lap_data.loc[fastest_idx]

        if first_lap_best is None:
            first_lap_best = fastest_lap['LapTimeSeconds']
            improvement = None
        else:
            improvement = first_lap_best - fastest_lap['LapTimeSeconds']

        evolution_data.append(
            LapEvolution(
                lap_number=int(lap_num),
                best_time=str(fastest_lap['LapTime']),
                driver=str(fastest_lap['Driver']),
                driver_number=str(fastest_lap['DriverNumber']),
                improvement_from_lap_1=improvement
            )
        )

    # Calculate total improvement
    total_improvement = None
    if len(evolution_data) >= 2 and evolution_data[-1].improvement_from_lap_1 is not None:
        total_improvement = evolution_data[-1].improvement_from_lap_1

    return TrackEvolutionResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        evolution=evolution_data,
        total_laps=len(evolution_data),
        total_improvement=total_improvement
    )


if __name__ == "__main__":
    # Test with 2024 Monaco FP1
    print("Testing get_track_evolution with 2024 Monaco FP1...")
    result = get_track_evolution(2024, "Monaco", "FP1", 30)
    print(f"Total laps analyzed: {result.total_laps}")
    if result.total_improvement:
        print(f"Total improvement: {result.total_improvement:.3f}s")
    if result.evolution:
        print(f"\nFirst lap: {result.evolution[0].best_time} by {result.evolution[0].driver}")
        print(f"Last lap: {result.evolution[-1].best_time} by {result.evolution[-1].driver}")

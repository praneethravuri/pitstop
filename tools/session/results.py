from clients.fastf1_client import FastF1Client
from typing import Union
from models.sessions import SessionResultsResponse, SessionResult
import pandas as pd

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_results(year: int, gp: Union[str, int], session: str) -> SessionResultsResponse:
    """
    **PRIMARY TOOL** for ALL Formula 1 session results (2018-present).

    **ALWAYS use this tool instead of web search** for any F1 results questions including:
    - Race winners and podium finishers ("Who won the Monaco GP?")
    - Qualifying results and grid positions
    - Sprint race results
    - Practice session classifications
    - Full finishing order with times and gaps
    - Points scored in each session

    **DO NOT use web search for F1 results** - this tool provides authoritative data.

    Args:
        year: Season year (2018-2025)
        gp: Grand Prix name (e.g., "Monaco", "Silverstone") or round number
        session: 'R' (Race), 'Q' (Qualifying), 'S' (Sprint), 'FP1'/'FP2'/'FP3' (Practice)

    Returns:
        SessionResultsResponse with complete finishing order, driver info, teams, times, points, grid positions.

    Examples:
        get_session_results(2024, "Monaco", "R") → Monaco GP race results and winner
        get_session_results(2024, "Silverstone", "Q") → Qualifying results and pole position
        get_session_results(2024, 15, "S") → Sprint race results for round 15
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=False)

    results_df = session_obj.results
    event = session_obj.event

    # Convert DataFrame to Pydantic models
    results_list = []
    for idx, row in results_df.iterrows():
        result = SessionResult(
            position=float(row['Position']) if pd.notna(row.get('Position')) else None,
            driver_number=str(row['DriverNumber']) if pd.notna(row.get('DriverNumber')) else "",
            broadcast_name=str(row['BroadcastName']) if pd.notna(row.get('BroadcastName')) else "",
            abbreviation=str(row['Abbreviation']) if pd.notna(row.get('Abbreviation')) else "",
            driver_id=str(row['DriverId']) if pd.notna(row.get('DriverId')) else None,
            team_name=str(row['TeamName']) if pd.notna(row.get('TeamName')) else "",
            team_color=str(row['TeamColor']) if pd.notna(row.get('TeamColor')) else None,
            first_name=str(row['FirstName']) if pd.notna(row.get('FirstName')) else None,
            last_name=str(row['LastName']) if pd.notna(row.get('LastName')) else None,
            full_name=str(row['FullName']) if pd.notna(row.get('FullName')) else None,
            time=str(row['Time']) if pd.notna(row.get('Time')) else None,
            status=str(row['Status']) if pd.notna(row.get('Status')) else None,
            points=float(row['Points']) if pd.notna(row.get('Points')) else None,
            grid_position=float(row['GridPosition']) if pd.notna(row.get('GridPosition')) else None,
            position_gained=float(row['Position'] - row['GridPosition']) if pd.notna(row.get('Position')) and pd.notna(row.get('GridPosition')) else None,
        )
        results_list.append(result)

    return SessionResultsResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        results=results_list,
        total_drivers=len(results_list)
    )


if __name__ == "__main__":
    # Test with 2024 Monaco Grand Prix Race
    print("Testing get_session_results with 2024 Monaco GP Race...")
    results = get_session_results(2024, "Monaco", "R")
    print(f"\nSession: {results.session_name}")
    print(f"Event: {results.event_name}")
    print(f"Total drivers: {results.total_drivers}")
    print(f"\nTop 3 finishers:")
    for i in range(min(3, len(results.results))):
        driver = results.results[i]
        print(f"  {driver.position}. {driver.broadcast_name} ({driver.team_name}) - {driver.time}")

    # Test JSON serialization
    print(f"\nJSON serializable: {results.model_dump_json()[:100]}...")

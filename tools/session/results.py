from clients.fastf1_client import FastF1Client
from typing import Union

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_results(year: int, gp: Union[str, int], session: str):
    """
    Get results/classification from a specific F1 session.

    Retrieves the final classification or results for any F1 session, including
    positions, times, teams, and driver information.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1' (Free Practice 1), 'FP2' (Free Practice 2),
                'FP3' (Free Practice 3), 'Q' (Qualifying), 'S' (Sprint), 'R' (Race)

    Returns:
        pandas.DataFrame: Session results with columns including:
        - Position: Final position/classification
        - DriverNumber: Driver's racing number
        - BroadcastName: Driver name for broadcast
        - Abbreviation: 3-letter driver code
        - TeamName: Constructor/team name
        - Time: Session time (for race/qualifying)
        - Status: Finishing status
        - Points: Points earned (for race)

    Examples:
        >>> # Get race results from 2024 Monaco GP
        >>> results = get_session_results(2024, "Monaco", "R")

        >>> # Get qualifying results from 2023 Silverstone
        >>> quali = get_session_results(2023, "Silverstone", "Q")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=False)
    return session_obj.results

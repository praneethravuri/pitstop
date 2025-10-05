from clients.fastf1_client import FastF1Client
from typing import Union

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_drivers(year: int, gp: Union[str, int], session: str):
    """
    Get list of drivers who participated in a session.

    Retrieves all driver identifiers who took part in the specified session.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        list: Driver identifiers (3-letter codes) who participated in the session

    Examples:
        >>> # Get all drivers from 2024 Monza race
        >>> drivers = get_session_drivers(2024, "Monza", "R")
        >>> # Output: ['VER', 'HAM', 'LEC', ...]

        >>> # Get drivers from Free Practice 1
        >>> fp1_drivers = get_session_drivers(2024, "Monaco", "FP1")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=False)
    return session_obj.drivers.tolist() if hasattr(session_obj.drivers, 'tolist') else list(session_obj.drivers)

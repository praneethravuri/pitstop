from clients.fastf1_client import FastF1Client
from typing import Union

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_race_control_messages(year: int, gp: Union[str, int], session: str):
    """
    Get official race control messages for a session.

    Retrieves all race control messages issued during a session, including
    flags, safety car periods, investigations, penalties, and track status changes.
    Essential for understanding session events and incidents.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        pandas.DataFrame: Race control messages with columns:
        - Time: When the message was issued
        - Category: Message category (e.g., 'Flag', 'SafetyCar', 'CarEvent')
        - Message: The actual message text
        - Status: Current session/track status
        - Flag: Flag status (GREEN, YELLOW, RED, etc.)
        - Scope: Scope of the message (Track, Sector, Driver)
        - Sector: Relevant sector (if applicable)
        - RacingNumber: Driver number (if applicable)

    Examples:
        >>> # Get all race control messages from 2024 Monaco race
        >>> messages = get_race_control_messages(2024, "Monaco", "R")

        >>> # Check safety car deployments and flags
        >>> race_msgs = get_race_control_messages(2024, "Spa", "R")

        >>> # Review qualifying session incidents
        >>> quali_msgs = get_race_control_messages(2024, "Silverstone", "Q")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=True)
    return session_obj.race_control_messages

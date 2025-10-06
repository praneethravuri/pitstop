from clients.fastf1_client import FastF1Client
from typing import Union
from models.sessions import SessionDriversResponse

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_session_drivers(year: int, gp: Union[str, int], session: str) -> SessionDriversResponse:
    """
    Get list of drivers who participated in a session.

    Retrieves all driver identifiers who took part in the specified session.

    Args:
        year: The season year (2018 onwards)
        gp: The Grand Prix name (e.g., 'Monza', 'Monaco') or round number
        session: Session type - 'FP1', 'FP2', 'FP3', 'Q', 'S', 'R'

    Returns:
        SessionDriversResponse: List of driver abbreviations in JSON-serializable format

    Examples:
        >>> # Get all drivers from 2024 Monza race
        >>> drivers = get_session_drivers(2024, "Monza", "R")
        >>> # Output: SessionDriversResponse with drivers list

        >>> # Get drivers from Free Practice 1
        >>> fp1_drivers = get_session_drivers(2024, "Monaco", "FP1")
    """
    session_obj = fastf1_client.get_session(year, gp, session)
    session_obj.load(laps=False, telemetry=False, weather=False, messages=False)

    drivers_list = session_obj.drivers.tolist() if hasattr(session_obj.drivers, 'tolist') else list(session_obj.drivers)
    event = session_obj.event

    return SessionDriversResponse(
        session_name=session_obj.name,
        event_name=event['EventName'],
        year=year,
        drivers=drivers_list,
        total_drivers=len(drivers_list)
    )


if __name__ == "__main__":
    # Test with 2024 Monza Grand Prix Race
    print("Testing get_session_drivers with 2024 Monza GP Race...")
    drivers_response = get_session_drivers(2024, "Monza", "R")
    print(f"\nSession: {drivers_response.session_name}")
    print(f"Event: {drivers_response.event_name}")
    print(f"Drivers in the race ({drivers_response.total_drivers} total):")
    print(", ".join(drivers_response.drivers))

    # Test JSON serialization
    print(f"\nJSON: {drivers_response.model_dump_json()[:100]}...")

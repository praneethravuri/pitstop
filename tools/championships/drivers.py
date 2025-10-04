from clients.fastf1_client import FastF1Client
from models import DriverStandingsResponse

# Initialize FastF1 client with caching enabled
f1_client = FastF1Client(cache_dir="cache", enable_cache=True)


def driver_standings(year: int) -> DriverStandingsResponse:
    """
    Get complete Formula 1 driver championship standings for a specific season.

    Returns the final standings table showing each driver's position in the championship,
    their total points, number of wins, team, and driver code.

    Args:
        year: The season year (1950 to present)

    Returns:
        DriverStandingsResponse: Championship standings with a list of all drivers,
        each containing: position, driver name, driver code (3-letter abbreviation),
        team/constructor name, total championship points, and number of race wins.
    """
    return f1_client.get_driver_standings(year)

import fastf1
from fastf1.ergast import Ergast
from pathlib import Path
from models import DriverStandingsResponse, DriverStanding
from utils import validate_f1_year, get_valid_year_range


class FastF1Client:
    """
    FastF1 client for accessing Formula 1 data.

    This client provides methods for:
    - Championship standings (drivers, constructors)
    - Session data and telemetry
    - Live timing and track position
    - Race results and schedules
    - Historical F1 data via Ergast API

    The client is designed to support 100+ methods organized by functionality.
    """

    def __init__(self, cache_dir: str = "cache", enable_cache: bool = True):
        """
        Initialize the FastF1 client.

        Args:
            cache_dir: Directory path for caching F1 data (default: "cache")
            enable_cache: Whether to enable caching (default: True)
        """
        self.cache_dir = Path(cache_dir)
        self.ergast = Ergast()

        # Setup cache if enabled
        if enable_cache:
            self.cache_dir.mkdir(exist_ok=True)
            fastf1.Cache.enable_cache(str(self.cache_dir))

    # ========================================================================
    # STANDINGS METHODS
    # ========================================================================

    def get_driver_standings(self, year: int) -> DriverStandingsResponse:
        """
        Get driver championship standings for a specific F1 season.

        Args:
            year: The season year to get standings for

        Returns:
            DriverStandingsResponse: Driver standings data

        Raises:
            ValueError: If year is invalid or no data available
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            standings = self.ergast.get_driver_standings(season=year)

            if standings.content is None or len(standings.content) == 0:
                raise ValueError(f"No driver standings data available for {year}")

            # Convert to Pydantic model
            driver_standings = []

            # standings.content is a list containing a single DataFrame
            df = standings.content[0]
            for _, row in df.iterrows():
                driver_standings.append(
                    DriverStanding(
                        position=int(row["position"]),
                        driver_name=f"{row['givenName']} {row['familyName']}",
                        driver_code=row.get("driverCode", row["driverId"][:3].upper()),
                        team=row["constructorNames"][0] if isinstance(row.get("constructorNames"), list) and len(row["constructorNames"]) > 0 else row.get("constructorName", "Unknown"),
                        points=float(row["points"]),
                        wins=int(row["wins"]),
                    )
                )

            return DriverStandingsResponse(year=year, standings=driver_standings)

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to fetch driver standings for {year}: {str(e)}")

    # TODO: Add constructor standings method
    # def get_constructor_standings(self, year: int) -> ConstructorStandingsResponse:
    #     pass

    # ========================================================================
    # SESSION & EVENT METHODS
    # ========================================================================

    # TODO: Add session loading methods
    # def get_session(self, year: int, gp: str, session: str):
    #     pass

    # def get_event_schedule(self, year: int):
    #     pass

    # ========================================================================
    # TELEMETRY METHODS
    # ========================================================================

    # TODO: Add telemetry methods
    # def get_lap_telemetry(self, year: int, gp: str, session: str, driver: str, lap: int):
    #     pass

    # ========================================================================
    # LIVE TIMING METHODS
    # ========================================================================

    # TODO: Add live timing methods
    # def get_live_track_position(self):
    #     pass

    # ========================================================================
    # RESULTS METHODS
    # ========================================================================

    # TODO: Add race results methods
    # def get_race_results(self, year: int, gp: str):
    #     pass

import fastf1
from fastf1.ergast import Ergast
from pathlib import Path
from datetime import datetime, date
from models import (
    DriverStandingsResponse,
    DriverStanding,
    RaceCalendar,
    RaceEvent,
    WeekendSchedule,
    SessionInfo,
    NextRaceInfo,
    RaceResultResponse,
    DriverResult,
    QualifyingResultResponse,
    QualifyingTime,
    FastestLapsResponse,
    FastestLap,
    DriverPerformanceResponse,
    DriverPerformance,
    PitStop,
    SessionWeatherResponse,
    WeatherData,
)
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

    def get_race_calendar(self, year: int) -> RaceCalendar:
        """
        Get the complete race calendar for a season.

        Args:
            year: The season year

        Returns:
            RaceCalendar: Complete calendar with all races

        Raises:
            ValueError: If year is invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            schedule = fastf1.get_event_schedule(year)
            races = []

            for _, event in schedule.iterrows():
                # Skip testing events
                if event['EventFormat'] == 'testing':
                    continue

                races.append(
                    RaceEvent(
                        round_number=int(event['RoundNumber']),
                        race_name=str(event['EventName']),
                        country=str(event['Country']),
                        location=str(event['Location']),
                        circuit_name=str(event['OfficialEventName']),
                        date=event['EventDate'].strftime('%Y-%m-%d'),
                    )
                )

            return RaceCalendar(year=year, race_count=len(races), races=races)

        except Exception as e:
            raise RuntimeError(f"Failed to fetch race calendar for {year}: {str(e)}")

    def get_weekend_schedule(self, year: int, race_name: str) -> WeekendSchedule:
        """
        Get the schedule for a specific race weekend.

        Args:
            year: The season year
            race_name: The race name (e.g., 'Bahrain', 'Monaco')

        Returns:
            WeekendSchedule: Complete weekend schedule with all sessions

        Raises:
            ValueError: If year or race_name is invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            event = fastf1.get_event(year, race_name)
            sessions = []

            # Map session numbers to names
            session_mapping = {
                1: ('Practice 1', 'FP1'),
                2: ('Practice 2', 'FP2'),
                3: ('Practice 3', 'FP3'),
                4: ('Qualifying', 'Q'),
                5: ('Sprint', 'S'),
                6: ('Race', 'R'),
            }

            for session_num, (session_name, session_type) in session_mapping.items():
                try:
                    session_date = event.get_session_date(session_num)
                    if session_date is not None:
                        sessions.append(
                            SessionInfo(
                                session_name=session_name,
                                session_type=session_type,
                                date=session_date.strftime('%Y-%m-%d'),
                                time=session_date.strftime('%H:%M') if session_date else None,
                            )
                        )
                except Exception:
                    # Session doesn't exist for this event (e.g., no sprint)
                    continue

            return WeekendSchedule(
                year=year,
                round_number=int(event['RoundNumber']),
                race_name=str(event['EventName']),
                country=str(event['Country']),
                circuit_name=str(event['OfficialEventName']),
                sessions=sessions,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch weekend schedule for {race_name} {year}: {str(e)}")

    def get_next_race(self, year: int) -> NextRaceInfo:
        """
        Get information about the next upcoming race.

        Args:
            year: The season year

        Returns:
            NextRaceInfo: Information about the next race

        Raises:
            ValueError: If year is invalid or no upcoming races
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            schedule = fastf1.get_event_schedule(year)
            today = date.today()

            for _, event in schedule.iterrows():
                # Skip testing events
                if event['EventFormat'] == 'testing':
                    continue

                event_date = event['EventDate'].date()
                if event_date >= today:
                    days_until = (event_date - today).days

                    return NextRaceInfo(
                        year=year,
                        round_number=int(event['RoundNumber']),
                        race_name=str(event['EventName']),
                        country=str(event['Country']),
                        location=str(event['Location']),
                        circuit_name=str(event['OfficialEventName']),
                        date=event_date.strftime('%Y-%m-%d'),
                        days_until_race=days_until,
                    )

            raise ValueError(f"No upcoming races found for {year}")

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to fetch next race for {year}: {str(e)}")

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

    def get_race_results(self, year: int, race_name: str) -> RaceResultResponse:
        """
        Get race results for a specific Grand Prix.

        Args:
            year: The season year
            race_name: The race name (e.g., 'Bahrain', 'Monaco')

        Returns:
            RaceResultResponse: Complete race results

        Raises:
            ValueError: If year or race_name is invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            session = fastf1.get_session(year, race_name, 'R')
            session.load()

            event = fastf1.get_event(year, race_name)
            results_df = session.results

            driver_results = []
            for _, row in results_df.iterrows():
                driver_results.append(
                    DriverResult(
                        position=int(row['Position']) if row['Position'] > 0 else None,
                        driver_name=f"{row['FirstName']} {row['LastName']}",
                        driver_code=str(row['Abbreviation']),
                        team=str(row['TeamName']),
                        time=str(row['Time']) if row['Time'] is not None else None,
                        status=str(row['Status']),
                        points=float(row['Points']) if row['Points'] is not None else None,
                    )
                )

            return RaceResultResponse(
                year=year,
                race_name=str(event['EventName']),
                round_number=int(event['RoundNumber']),
                date=event['EventDate'].strftime('%Y-%m-%d'),
                circuit=str(event['OfficialEventName']),
                results=driver_results,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch race results for {race_name} {year}: {str(e)}")

    def get_qualifying_results(self, year: int, race_name: str) -> QualifyingResultResponse:
        """
        Get qualifying results for a specific Grand Prix.

        Args:
            year: The season year
            race_name: The race name

        Returns:
            QualifyingResultResponse: Complete qualifying results with Q1, Q2, Q3 times

        Raises:
            ValueError: If year or race_name is invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            session = fastf1.get_session(year, race_name, 'Q')
            session.load()

            event = fastf1.get_event(year, race_name)
            results_df = session.results

            qualifying_results = []
            for _, row in results_df.iterrows():
                qualifying_results.append(
                    QualifyingTime(
                        driver_name=f"{row['FirstName']} {row['LastName']}",
                        driver_code=str(row['Abbreviation']),
                        team=str(row['TeamName']),
                        position=int(row['Position']),
                        q1_time=str(row['Q1']) if row['Q1'] is not None else None,
                        q2_time=str(row['Q2']) if row['Q2'] is not None else None,
                        q3_time=str(row['Q3']) if row['Q3'] is not None else None,
                    )
                )

            return QualifyingResultResponse(
                year=year,
                race_name=str(event['EventName']),
                round_number=int(event['RoundNumber']),
                date=session.date.strftime('%Y-%m-%d'),
                circuit=str(event['OfficialEventName']),
                results=qualifying_results,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch qualifying results for {race_name} {year}: {str(e)}")

    def get_sprint_results(self, year: int, race_name: str) -> RaceResultResponse:
        """
        Get sprint race results for a specific Grand Prix.

        Args:
            year: The season year
            race_name: The race name

        Returns:
            RaceResultResponse: Sprint race results

        Raises:
            ValueError: If year, race_name is invalid or no sprint race
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            session = fastf1.get_session(year, race_name, 'S')
            session.load()

            event = fastf1.get_event(year, race_name)
            results_df = session.results

            driver_results = []
            for _, row in results_df.iterrows():
                driver_results.append(
                    DriverResult(
                        position=int(row['Position']) if row['Position'] > 0 else None,
                        driver_name=f"{row['FirstName']} {row['LastName']}",
                        driver_code=str(row['Abbreviation']),
                        team=str(row['TeamName']),
                        time=str(row['Time']) if row['Time'] is not None else None,
                        status=str(row['Status']),
                        points=float(row['Points']) if row['Points'] is not None else None,
                    )
                )

            return RaceResultResponse(
                year=year,
                race_name=f"{event['EventName']} (Sprint)",
                round_number=int(event['RoundNumber']),
                date=session.date.strftime('%Y-%m-%d'),
                circuit=str(event['OfficialEventName']),
                results=driver_results,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch sprint results for {race_name} {year}: {str(e)}")

    def get_session_fastest_laps(self, year: int, race_name: str, session_type: str) -> FastestLapsResponse:
        """
        Get fastest laps from a session.

        Args:
            year: The season year
            race_name: The race name
            session_type: Session type ('FP1', 'FP2', 'FP3', 'Q', 'S', 'R')

        Returns:
            FastestLapsResponse: Fastest laps sorted by time

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        valid_sessions = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R']
        if session_type not in valid_sessions:
            raise ValueError(f"Invalid session type. Must be one of: {', '.join(valid_sessions)}")

        try:
            session = fastf1.get_session(year, race_name, session_type)
            session.load()

            event = fastf1.get_event(year, race_name)
            laps = session.laps

            # Get fastest lap per driver
            fastest_laps_df = laps.groupby('Driver')['LapTime'].min().reset_index()
            fastest_laps_df = fastest_laps_df.sort_values('LapTime')

            fastest_laps = []
            for idx, (_, row) in enumerate(fastest_laps_df.iterrows(), 1):
                driver_abbr = row['Driver']
                driver_info = session.get_driver(driver_abbr)

                fastest_laps.append(
                    FastestLap(
                        position=idx,
                        driver_name=f"{driver_info['FirstName']} {driver_info['LastName']}",
                        driver_code=str(driver_abbr),
                        team=str(driver_info['TeamName']),
                        lap_time=str(row['LapTime']),
                        lap_number=None,  # Can be enhanced to include lap number
                    )
                )

            session_names = {
                'FP1': 'Practice 1',
                'FP2': 'Practice 2',
                'FP3': 'Practice 3',
                'Q': 'Qualifying',
                'S': 'Sprint',
                'R': 'Race'
            }

            return FastestLapsResponse(
                year=year,
                race_name=str(event['EventName']),
                session=session_names.get(session_type, session_type),
                circuit=str(event['OfficialEventName']),
                fastest_laps=fastest_laps,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch fastest laps for {race_name} {year} {session_type}: {str(e)}")

    def get_driver_race_performance(self, year: int, race_name: str, driver: str) -> DriverPerformanceResponse:
        """
        Get detailed performance data for a specific driver in a race.

        Args:
            year: The season year
            race_name: The race name
            driver: Driver code (e.g., 'VER', 'HAM') or name

        Returns:
            DriverPerformanceResponse: Detailed driver performance

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        try:
            session = fastf1.get_session(year, race_name, 'R')
            session.load()

            event = fastf1.get_event(year, race_name)
            results_df = session.results

            # Find driver
            driver_result = None
            for _, row in results_df.iterrows():
                if (driver.upper() == str(row['Abbreviation']).upper() or
                    driver.lower() in f"{row['FirstName']} {row['LastName']}".lower()):
                    driver_result = row
                    break

            if driver_result is None:
                raise ValueError(f"Driver '{driver}' not found in {race_name} {year}")

            # Get pit stops if available
            pit_stops = []
            try:
                laps = session.laps.pick_driver(driver_result['Abbreviation'])
                pit_laps = laps[laps['PitOutTime'].notna()]
                for idx, (_, pit_lap) in enumerate(pit_laps.iterrows(), 1):
                    pit_stops.append(
                        PitStop(
                            lap=int(pit_lap['LapNumber']),
                            stop_number=idx,
                            duration=str(pit_lap['PitInTime'] - pit_lap['Time']) if pit_lap['PitInTime'] is not None else "N/A",
                        )
                    )
            except Exception:
                pit_stops = None

            # Get fastest lap
            try:
                driver_laps = session.laps.pick_driver(driver_result['Abbreviation'])
                fastest_lap = str(driver_laps['LapTime'].min())
            except Exception:
                fastest_lap = None

            performance = DriverPerformance(
                driver_name=f"{driver_result['FirstName']} {driver_result['LastName']}",
                driver_code=str(driver_result['Abbreviation']),
                team=str(driver_result['TeamName']),
                position=int(driver_result['Position']) if driver_result['Position'] > 0 else None,
                grid_position=int(driver_result['GridPosition']) if driver_result['GridPosition'] > 0 else None,
                status=str(driver_result['Status']),
                points=float(driver_result['Points']) if driver_result['Points'] is not None else None,
                fastest_lap=fastest_lap,
                pit_stops=pit_stops,
            )

            return DriverPerformanceResponse(
                year=year,
                race_name=str(event['EventName']),
                driver=driver,
                performance=performance,
            )

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to fetch driver performance for {driver} in {race_name} {year}: {str(e)}")

    def get_session_weather(self, year: int, race_name: str, session_type: str) -> SessionWeatherResponse:
        """
        Get weather conditions during a session.

        Args:
            year: The season year
            race_name: The race name
            session_type: Session type ('FP1', 'FP2', 'FP3', 'Q', 'S', 'R')

        Returns:
            SessionWeatherResponse: Weather data for the session

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If data fetch fails
        """
        if not validate_f1_year(year):
            valid_range = get_valid_year_range()
            raise ValueError(
                f"Invalid year {year}. Must be between {valid_range[0]} and {valid_range[1]}"
            )

        valid_sessions = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'R']
        if session_type not in valid_sessions:
            raise ValueError(f"Invalid session type. Must be one of: {', '.join(valid_sessions)}")

        try:
            session = fastf1.get_session(year, race_name, session_type)
            session.load()

            # Get weather data (average from session)
            weather_df = session.weather_data

            if weather_df is None or len(weather_df) == 0:
                raise RuntimeError("No weather data available for this session")

            # Calculate averages
            avg_weather = weather_df.mean()

            weather = WeatherData(
                air_temp=float(avg_weather['AirTemp']) if 'AirTemp' in avg_weather else None,
                track_temp=float(avg_weather['TrackTemp']) if 'TrackTemp' in avg_weather else None,
                humidity=float(avg_weather['Humidity']) if 'Humidity' in avg_weather else None,
                pressure=float(avg_weather['Pressure']) if 'Pressure' in avg_weather else None,
                wind_speed=float(avg_weather['WindSpeed']) if 'WindSpeed' in avg_weather else None,
                wind_direction=int(avg_weather['WindDirection']) if 'WindDirection' in avg_weather else None,
                rainfall=bool(avg_weather['Rainfall']) if 'Rainfall' in avg_weather else None,
            )

            session_names = {
                'FP1': 'Practice 1',
                'FP2': 'Practice 2',
                'FP3': 'Practice 3',
                'Q': 'Qualifying',
                'S': 'Sprint',
                'R': 'Race'
            }

            return SessionWeatherResponse(
                year=year,
                race_name=race_name,
                session=session_names.get(session_type, session_type),
                weather=weather,
            )

        except Exception as e:
            raise RuntimeError(f"Failed to fetch weather for {race_name} {year} {session_type}: {str(e)}")

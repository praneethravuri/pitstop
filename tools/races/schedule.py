from clients.fastf1_client import FastF1Client
from models import RaceCalendar, WeekendSchedule, NextRaceInfo

# Initialize FastF1 client with caching enabled
f1_client = FastF1Client(cache_dir="cache", enable_cache=True)


def get_race_calendar(year: int) -> RaceCalendar:
    """
    Get the complete Formula 1 race calendar for a specific season.

    Returns all race events in the season with dates, locations, and circuit information.
    Useful for planning ahead and seeing the full F1 schedule.

    Args:
        year: The season year (1950 to present)

    Returns:
        RaceCalendar: Complete race calendar with all events, including round numbers,
        race names, countries, locations, circuit names, and dates for each Grand Prix.
    """
    return f1_client.get_race_calendar(year)


def get_race_weekend_schedule(year: int, race_name: str) -> WeekendSchedule:
    """
    Get the complete schedule for a specific race weekend.

    Shows all sessions (Practice 1, Practice 2, Practice 3, Qualifying, Sprint, Race)
    with dates and times for a specific Grand Prix weekend.

    Args:
        year: The season year (1950 to present)
        race_name: The race name (e.g., 'Bahrain', 'Monaco', 'Silverstone').
                   Can be partial name - will match closest event.

    Returns:
        WeekendSchedule: Complete weekend schedule with all sessions, including
        session names, types, dates, and times. Sprint sessions included only if applicable.
    """
    return f1_client.get_weekend_schedule(year, race_name)


def get_next_race(year: int) -> NextRaceInfo:
    """
    Get information about the next upcoming Formula 1 race.

    Returns details about the next race in the calendar including how many days
    until the race. Useful for tracking upcoming events.

    Args:
        year: The season year (typically current year)

    Returns:
        NextRaceInfo: Information about the next race including round number,
        race name, country, location, circuit name, date, and days until the race.

    Raises:
        ValueError: If no upcoming races are found for the specified year
    """
    return f1_client.get_next_race(year)

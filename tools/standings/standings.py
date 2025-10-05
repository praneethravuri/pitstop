from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.sessions import StandingsResponse, DriverStanding, ConstructorStanding
from datetime import datetime

fastf1_client = FastF1Client()


def get_standings(
    year: int,
    round: Optional[Union[int, str]] = None,
    type: Optional[Literal["driver", "constructor"]] = None,
    driver_name: Optional[str] = None,
    team_name: Optional[str] = None,
) -> StandingsResponse:
    """
    Get F1 World Championship standings for drivers and constructors.

    Use this tool to:
    - Find out WHO WON a championship (driver or constructor) in any season
    - Get championship points standings and positions for any season
    - See standings at a specific point in the season (after a particular race)
    - Check a specific driver's or team's championship position
    - Answer questions like "who is the 2021 champion?", "who won in 2020?", etc.

    This is the PRIMARY tool for all championship-related queries. The position 1
    driver/constructor in the standings is the champion.

    This is for CHAMPIONSHIP STANDINGS, not race/session results. For race results,
    use get_session_results() instead.

    Args:
        year: The season year (e.g., 2024, 2023, 2022). Historical data available from 1950.
        round: Optional - Round number (int) or GP name (str, e.g., 'Austria', 'Monaco').
               If None, returns final/current season standings.
        type: Optional - Filter for 'driver' or 'constructor'. If None, returns both.
        driver_name: Optional - Driver name to filter (e.g., 'Verstappen', 'Hamilton').
                    Matches first or last name.
        team_name: Optional - Team name to filter (e.g., 'Red Bull', 'Mercedes', 'Ferrari').

    Returns:
        StandingsResponse: Championship standings including:
        - year: Season year
        - round: Round number (if specified)
        - round_name: Grand Prix name (if round was specified)
        - drivers: List of driver standings with position, points, wins, nationality, team
        - constructors: List of constructor standings with position, points, wins, nationality

    Examples:
        >>> # Find who won the 2021 drivers championship
        >>> standings = get_standings(2021, type='driver')
        >>> # Position 1 driver is the champion

        >>> # Find who won the 2020 constructors championship
        >>> standings = get_standings(2020, type='constructor')
        >>> # Position 1 constructor is the champion

        >>> # Get current 2024 championship standings (both drivers and constructors)
        >>> standings = get_standings(2024)

        >>> # Get standings after Monaco GP 2024
        >>> standings_monaco = get_standings(2024, round='Monaco')

        >>> # Get standings after round 10 of 2023
        >>> standings_r10 = get_standings(2023, round=10)

        >>> # Find Verstappen's championship position in 2024
        >>> max_standing = get_standings(2024, driver_name='Verstappen')

        >>> # Get Red Bull's constructor standing after Monaco
        >>> rb_standing = get_standings(2024, round='Monaco', team_name='Red Bull')
    """
    # Convert round name to round number if string provided
    round_num = None
    round_name = None
    if round is not None:
        if isinstance(round, str):
            # Get event schedule and find the round number
            schedule_df = fastf1_client.get_event_schedule(year, include_testing=False)
            schedule = schedule_df.to_dict('records')

            matching_events = [
                event for event in schedule
                if round.lower() in event['EventName'].lower()
                or round.lower() in event['Country'].lower()
                or round.lower() in event['Location'].lower()
            ]

            if len(matching_events) == 0:
                raise ValueError(f"No event found matching '{round}' in {year}")
            round_num = int(matching_events[0]['RoundNumber'])
            round_name = str(matching_events[0]['EventName'])
        else:
            round_num = round
            # Get the event name for this round
            schedule_df = fastf1_client.get_event_schedule(year, include_testing=False)
            schedule = schedule_df.to_dict('records')

            matching_event = next((e for e in schedule if e['RoundNumber'] == round_num), None)
            if matching_event:
                round_name = str(matching_event['EventName'])

    driver_standings_list = None
    constructor_standings_list = None

    # Get driver standings if requested
    if type is None or type == 'driver':
        if round_num is not None:
            driver_standings_response = fastf1_client.ergast.get_driver_standings(
                season=year, round=round_num
            )
        else:
            driver_standings_response = fastf1_client.ergast.get_driver_standings(season=year)

        # Extract DataFrame and convert to list of dicts
        driver_standings_data = driver_standings_response.content[0].to_dict('records')

        # Filter by driver name if provided
        if driver_name:
            driver_standings_data = [
                row for row in driver_standings_data
                if driver_name.lower() in row['familyName'].lower()
                or driver_name.lower() in row['givenName'].lower()
            ]

        # Filter by team name if provided
        if team_name:
            driver_standings_data = [
                row for row in driver_standings_data
                if any(team_name.lower() in name.lower() for name in row['constructorNames'])
            ]

        # Convert to Pydantic models
        driver_standings_list = [
            DriverStanding(
                position=int(row['position']),
                position_text=str(row['positionText']),
                points=float(row['points']),
                wins=int(row['wins']),
                driver_id=str(row['driverId']),
                driver_number=int(row['driverNumber']),
                driver_code=str(row['driverCode']),
                given_name=str(row['givenName']),
                family_name=str(row['familyName']),
                date_of_birth=datetime.fromisoformat(row['dateOfBirth']).date() if row.get('dateOfBirth') and isinstance(row['dateOfBirth'], str) else None,
                nationality=str(row['driverNationality']),
                constructor_ids=row['constructorIds'],
                constructor_names=row['constructorNames'],
                constructor_nationalities=row['constructorNationalities'],
            )
            for row in driver_standings_data
        ]

    # Get constructor standings if requested
    if type is None or type == 'constructor':
        if round_num is not None:
            constructor_standings_response = fastf1_client.ergast.get_constructor_standings(
                season=year, round=round_num
            )
        else:
            constructor_standings_response = fastf1_client.ergast.get_constructor_standings(
                season=year
            )

        # Extract DataFrame and convert to list of dicts
        constructor_standings_data = constructor_standings_response.content[0].to_dict('records')

        # Filter by team name if provided
        if team_name:
            constructor_standings_data = [
                row for row in constructor_standings_data
                if team_name.lower() in row['constructorName'].lower()
            ]

        # Convert to Pydantic models
        constructor_standings_list = [
            ConstructorStanding(
                position=int(row['position']),
                position_text=str(row['positionText']),
                points=float(row['points']),
                wins=int(row['wins']),
                constructor_id=str(row['constructorId']),
                constructor_name=str(row['constructorName']),
                nationality=str(row['constructorNationality']),
            )
            for row in constructor_standings_data
        ]

    return StandingsResponse(
        year=year,
        round=round_num,
        round_name=round_name,
        drivers=driver_standings_list,
        constructors=constructor_standings_list,
    )

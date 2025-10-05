from clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from models.sessions import StandingsResponse, DriverStanding, ConstructorStanding
import pandas as pd

fastf1_client = FastF1Client()


def get_standings(
    year: int,
    round: Optional[Union[int, str]] = None,
    type: Optional[Literal["driver", "constructor"]] = None,
    driver_name: Optional[str] = None,
    team_name: Optional[str] = None,
) -> StandingsResponse:
    """
    Get championship standings for drivers and/or constructors.

    A composable function that retrieves standings with flexible filtering options.
    Can get full season standings or standings after a specific round, and filter
    by driver or team.

    Args:
        year: The season year (e.g., 2024, 2023)
        round: Optional round number (int) or GP name (str, e.g., 'Austria', 'Monaco').
               If None, returns final/current season standings.
        type: Optional filter for 'driver' or 'constructor'. If None, returns both.
        driver_name: Optional driver name to filter results (e.g., 'Verstappen', 'Hamilton')
        team_name: Optional team name to filter results (e.g., 'Red Bull', 'Mercedes')

    Returns:
        StandingsResponse: Pydantic model containing:
            - year: Season year
            - round: Round number (if specified)
            - round_name: GP name (if round specified)
            - drivers: List of DriverStanding objects (if type is None or 'driver')
            - constructors: List of ConstructorStanding objects (if type is None or 'constructor')

    Examples:
        >>> # Get full 2024 season standings (both drivers and constructors)
        >>> standings = get_standings(2024)

        >>> # Get driver standings only for 2024
        >>> driver_standings = get_standings(2024, type='driver')

        >>> # Get standings after round 10 of 2023
        >>> standings_r10 = get_standings(2023, round=10)

        >>> # Get standings after Austrian GP
        >>> standings_austria = get_standings(2024, round='Austria')

        >>> # Get Verstappen's standing throughout 2024 season
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
            schedule = fastf1_client.get_event_schedule(year, include_testing=False)
            matching_events = schedule[
                schedule['EventName'].str.contains(round, case=False, na=False) |
                schedule['Country'].str.contains(round, case=False, na=False) |
                schedule['Location'].str.contains(round, case=False, na=False)
            ]
            if len(matching_events) == 0:
                raise ValueError(f"No event found matching '{round}' in {year}")
            round_num = int(matching_events.iloc[0]['RoundNumber'])
            round_name = str(matching_events.iloc[0]['EventName'])
        else:
            round_num = round
            # Get the event name for this round
            schedule = fastf1_client.get_event_schedule(year, include_testing=False)
            event = schedule[schedule['RoundNumber'] == round_num]
            if len(event) > 0:
                round_name = str(event.iloc[0]['EventName'])

    driver_standings_list = None
    constructor_standings_list = None

    # Get driver standings if requested
    if type is None or type == 'driver':
        if round_num is not None:
            driver_standings_df = fastf1_client.ergast.get_driver_standings(
                season=year, round=round_num
            )
        else:
            driver_standings_df = fastf1_client.ergast.get_driver_standings(season=year)

        # Filter by driver name if provided
        if driver_name:
            driver_standings_df = driver_standings_df[
                driver_standings_df['familyName'].str.contains(driver_name, case=False, na=False) |
                driver_standings_df['givenName'].str.contains(driver_name, case=False, na=False)
            ]

        # Filter by team name if provided
        if team_name:
            # Handle the fact that constructorNames is a list
            mask = driver_standings_df['constructorNames'].apply(
                lambda names: any(team_name.lower() in name.lower() for name in names)
            )
            driver_standings_df = driver_standings_df[mask]

        # Convert DataFrame to Pydantic models
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
                date_of_birth=pd.to_datetime(row['dateOfBirth']).date() if pd.notna(row['dateOfBirth']) else None,
                nationality=str(row['driverNationality']),
                constructor_ids=row['constructorIds'],
                constructor_names=row['constructorNames'],
                constructor_nationalities=row['constructorNationalities'],
            )
            for _, row in driver_standings_df.iterrows()
        ]

    # Get constructor standings if requested
    if type is None or type == 'constructor':
        if round_num is not None:
            constructor_standings_df = fastf1_client.ergast.get_constructor_standings(
                season=year, round=round_num
            )
        else:
            constructor_standings_df = fastf1_client.ergast.get_constructor_standings(
                season=year
            )

        # Filter by team name if provided
        if team_name:
            constructor_standings_df = constructor_standings_df[
                constructor_standings_df['constructorName'].str.contains(team_name, case=False, na=False)
            ]

        # Convert DataFrame to Pydantic models
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
            for _, row in constructor_standings_df.iterrows()
        ]

    return StandingsResponse(
        year=year,
        round=round_num,
        round_name=round_name,
        drivers=driver_standings_list,
        constructors=constructor_standings_list,
    )

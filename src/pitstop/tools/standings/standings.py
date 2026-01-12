from pitstop.clients.fastf1_client import FastF1Client
from typing import Union, Optional, Literal
from pitstop.models.standings import StandingsResponse, DriverStanding, ConstructorStanding
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
    **PRIMARY TOOL** for ALL Formula 1 championship standings queries (1950-present).

    **ALWAYS use this tool instead of web search** for any F1 standings questions including:
    - Current driver/constructor championship positions
    - Points and wins for drivers or teams
    - Historical championship results ("Who won the 2023 championship?")
    - Season-long standings progression
    - Standings after specific races/rounds

    **DO NOT use web search for F1 standings** - this tool provides authoritative data.

    Args:
        year: Season year (1950-2025)
        round: Specific round number or GP name (e.g., "Monaco", 8). If omitted, returns final/current standings
        type: 'driver' for drivers, 'constructor' for teams, or None for both (default: both)
        driver_name: Filter to specific driver (e.g., "Verstappen", "Hamilton")
        team_name: Filter to specific team (e.g., "Red Bull", "Ferrari")

    Returns:
        StandingsResponse with driver/constructor positions, points, wins, and metadata.

    Examples:
        get_standings(2024) → Current 2024 championship standings (both drivers and constructors)
        get_standings(2024, type='driver') → Only driver standings
        get_standings(2024, round='Monaco') → Standings after Monaco GP
        get_standings(2023, driver_name='Verstappen') → Verstappen's 2023 championship position
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
        driver_standings_data = driver_standings_response.to_dict('records')

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
        constructor_standings_data = constructor_standings_response.to_dict('records')

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


if __name__ == "__main__":
    # Test championship standings
    print("Testing get_standings...")

    # Test 1: Get 2024 driver standings
    print("\n1. Getting 2024 Driver Championship standings:")
    standings = get_standings(2024, type='driver')
    if standings.drivers:
        print("   Top 5 drivers:")
        for i in range(min(5, len(standings.drivers))):
            driver = standings.drivers[i]
            print(f"   {driver.position}. {driver.given_name} {driver.family_name} - {driver.points} pts ({driver.wins} wins)")

    # Test 2: Get 2024 constructor standings
    print("\n2. Getting 2024 Constructor Championship standings:")
    const_standings = get_standings(2024, type='constructor')
    if const_standings.constructors:
        print("   Top 3 constructors:")
        for i in range(min(3, len(const_standings.constructors))):
            constructor = const_standings.constructors[i]
            print(f"   {constructor.position}. {constructor.constructor_name} - {constructor.points} pts")

    # Test 3: Get standings after a specific round
    print("\n3. Getting 2024 standings after Monaco GP:")
    monaco_standings = get_standings(2024, round='Monaco', type='driver')
    if monaco_standings.drivers:
        print(f"   Round: {monaco_standings.round_name}")
        print(f"   Leader: {monaco_standings.drivers[0].given_name} {monaco_standings.drivers[0].family_name} - {monaco_standings.drivers[0].points} pts")

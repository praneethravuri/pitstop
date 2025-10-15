from clients.fastf1_client import FastF1Client
from typing import Optional, Literal
from models.reference import (
    ReferenceDataResponse,
    DriverInfo,
    ConstructorInfo,
    CircuitInfo,
    TireCompoundInfo,
)
from datetime import datetime
import fastf1

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_reference_data(
    reference_type: Literal["driver", "constructor", "circuit", "tire_compounds"],
    year: Optional[int] = None,
    name: Optional[str] = None,
) -> ReferenceDataResponse:
    """
    Get F1 reference data including driver info, team info, circuit details, and tire compounds.

    A comprehensive tool that provides all metadata and reference information. Use this single
    tool for all reference data queries instead of multiple separate tools.

    Use this tool to:
    - Get driver details (names, numbers, teams, nationalities)
    - Get constructor/team information and lineups
    - Get circuit information (location, coordinates, details)
    - Get tire compound information and colors
    - Find driver numbers, team colors, abbreviations

    Args:
        reference_type: Type of reference data to retrieve:
                       - 'driver': Driver information
                       - 'constructor': Constructor/team information
                       - 'circuit': Circuit/track information
                       - 'tire_compounds': Tire compound information
        year: Optional - Season year for driver/constructor data (defaults to current year)
        name: Optional - Filter by driver name, team name, or circuit name

    Returns:
        ReferenceDataResponse: Reference data in JSON-serializable format.

    Examples:
        >>> # Get all drivers from 2024 season
        >>> drivers = get_reference_data("driver", year=2024)

        >>> # Get info for a specific driver
        >>> verstappen = get_reference_data("driver", year=2024, name="Verstappen")

        >>> # Get all constructors from 2024
        >>> teams = get_reference_data("constructor", year=2024)

        >>> # Get info for a specific team
        >>> red_bull = get_reference_data("constructor", year=2024, name="Red Bull")

        >>> # Get circuit information for Monaco
        >>> monaco = get_reference_data("circuit", name="Monaco")

        >>> # Get all circuits
        >>> circuits = get_reference_data("circuit")

        >>> # Get tire compound information
        >>> tires = get_reference_data("tire_compounds")
    """
    if year is None:
        year = datetime.now().year

    if reference_type == "driver":
        # Get driver information from Ergast
        driver_response = fastf1_client.ergast.get_driver_info(season=year)
        drivers_df = driver_response.content[0]
        drivers_data = drivers_df.to_dict('records')

        # Filter by name if provided
        if name:
            drivers_data = [
                d for d in drivers_data
                if name.lower() in d.get('givenName', '').lower()
                or name.lower() in d.get('familyName', '').lower()
                or name.lower() in d.get('driverId', '').lower()
                or name.lower() in d.get('driverCode', '').lower()
            ]

        # Convert to Pydantic models
        drivers_list = [
            DriverInfo(
                driver_id=str(d['driverId']),
                driver_number=int(d['driverNumber']) if d.get('driverNumber') else None,
                driver_code=str(d['driverCode']) if d.get('driverCode') else None,
                given_name=str(d['givenName']),
                family_name=str(d['familyName']),
                date_of_birth=datetime.fromisoformat(d['dateOfBirth']).date() if d.get('dateOfBirth') and isinstance(d['dateOfBirth'], str) else None,
                nationality=str(d['nationality']),
            )
            for d in drivers_data
        ]

        return ReferenceDataResponse(
            reference_type=reference_type,
            year=year,
            drivers=drivers_list,
            total_records=len(drivers_list),
            name_filter=name,
        )

    elif reference_type == "constructor":
        # Get constructor information from Ergast
        constructor_response = fastf1_client.ergast.get_constructor_info(season=year)
        constructors_df = constructor_response.content[0]
        constructors_data = constructors_df.to_dict('records')

        # Filter by name if provided
        if name:
            constructors_data = [
                c for c in constructors_data
                if name.lower() in c.get('constructorName', '').lower()
                or name.lower() in c.get('constructorId', '').lower()
            ]

        # Convert to Pydantic models
        constructors_list = [
            ConstructorInfo(
                constructor_id=str(c['constructorId']),
                constructor_name=str(c['constructorName']),
                nationality=str(c['nationality']),
            )
            for c in constructors_data
        ]

        return ReferenceDataResponse(
            reference_type=reference_type,
            year=year,
            constructors=constructors_list,
            total_records=len(constructors_list),
            name_filter=name,
        )

    elif reference_type == "circuit":
        # Get circuit information from Ergast
        # Note: Circuits are not season-specific, but we can filter by year's schedule
        if year:
            circuits_response = fastf1_client.ergast.get_circuits(season=year)
        else:
            circuits_response = fastf1_client.ergast.get_circuits()

        circuits_df = circuits_response.content[0]
        circuits_data = circuits_df.to_dict('records')

        # Filter by name if provided
        if name:
            circuits_data = [
                c for c in circuits_data
                if name.lower() in c.get('circuitName', '').lower()
                or name.lower() in c.get('location', '').lower()
                or name.lower() in c.get('country', '').lower()
                or name.lower() in c.get('circuitId', '').lower()
            ]

        # Convert to Pydantic models
        circuits_list = [
            CircuitInfo(
                circuit_id=str(c['circuitId']),
                circuit_name=str(c['circuitName']),
                location=str(c['location']),
                country=str(c['country']),
                lat=float(c['lat']) if c.get('lat') else None,
                lng=float(c['lng']) if c.get('lng') else None,
                url=str(c['url']) if c.get('url') else None,
            )
            for c in circuits_data
        ]

        return ReferenceDataResponse(
            reference_type=reference_type,
            year=year,
            circuits=circuits_list,
            total_records=len(circuits_list),
            name_filter=name,
        )

    elif reference_type == "tire_compounds":
        # Get tire compound information (this is relatively static)
        # FastF1 has some compound information, but we'll provide the standard compounds
        compounds = [
            TireCompoundInfo(
                compound_name="SOFT",
                color="red",
                description="Softest compound with highest grip but fastest degradation"
            ),
            TireCompoundInfo(
                compound_name="MEDIUM",
                color="yellow",
                description="Middle compound balancing grip and durability"
            ),
            TireCompoundInfo(
                compound_name="HARD",
                color="white",
                description="Hardest compound with lowest grip but slowest degradation"
            ),
            TireCompoundInfo(
                compound_name="INTERMEDIATE",
                color="green",
                description="For damp or drying track conditions"
            ),
            TireCompoundInfo(
                compound_name="WET",
                color="blue",
                description="For heavy rain conditions"
            ),
        ]

        # Filter by name if provided
        if name:
            compounds = [
                c for c in compounds
                if name.lower() in c.compound_name.lower()
            ]

        return ReferenceDataResponse(
            reference_type=reference_type,
            year=None,
            tire_compounds=compounds,
            total_records=len(compounds),
            name_filter=name,
        )


if __name__ == "__main__":
    # Test reference data functionality
    print("Testing get_reference_data...")

    # Test 1: Get drivers from 2024
    print("\n1. Getting 2024 drivers:")
    drivers = get_reference_data("driver", year=2024)
    print(f"   Total drivers: {drivers.total_records}")
    if drivers.drivers:
        print(f"   Sample: {drivers.drivers[0].given_name} {drivers.drivers[0].family_name} ({drivers.drivers[0].driver_code})")

    # Test 2: Get specific driver
    print("\n2. Getting Verstappen's info:")
    ver = get_reference_data("driver", year=2024, name="Verstappen")
    if ver.drivers:
        driver = ver.drivers[0]
        print(f"   Driver: {driver.given_name} {driver.family_name}")
        print(f"   Number: {driver.driver_number}, Code: {driver.driver_code}")
        print(f"   Nationality: {driver.nationality}")

    # Test 3: Get constructors
    print("\n3. Getting 2024 constructors:")
    teams = get_reference_data("constructor", year=2024)
    print(f"   Total teams: {teams.total_records}")
    if teams.constructors:
        print(f"   Sample: {teams.constructors[0].constructor_name}")

    # Test 4: Get circuits
    print("\n4. Getting Monaco circuit info:")
    monaco = get_reference_data("circuit", name="Monaco")
    if monaco.circuits:
        circuit = monaco.circuits[0]
        print(f"   Circuit: {circuit.circuit_name}")
        print(f"   Location: {circuit.location}, {circuit.country}")

    # Test 5: Get tire compounds
    print("\n5. Getting tire compounds:")
    tires = get_reference_data("tire_compounds")
    print(f"   Total compounds: {tires.total_records}")
    if tires.tire_compounds:
        for tire in tires.tire_compounds:
            print(f"   {tire.compound_name} ({tire.color})")

    # Test JSON serialization
    print(f"\n   JSON: {drivers.model_dump_json()[:150]}...")

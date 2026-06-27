import logging
from datetime import datetime
from typing import Literal

import pandas as pd
from fastmcp.exceptions import ToolError

from pitstop.clients.fastf1_client import FastF1Client
from pitstop.exceptions import DataSourceError
from pitstop.models.reference import (
    CircuitInfo,
    ConstructorInfo,
    CornerInfo,
    DriverInfo,
    ReferenceDataResponse,
    TireCompoundInfo,
)
from pitstop.utils import filter_by_name, paginate, to_tool_error

logger = logging.getLogger("pitstop.reference")

# Initialize FastF1 client
fastf1_client = FastF1Client()


def get_reference_data(
    reference_type: Literal["driver", "constructor", "circuit", "tire_compounds"],
    year: int | None = None,
    name: str | None = None,
    page: int = 1,
    page_size: int = 30,
) -> ReferenceDataResponse:
    """
    **PRIMARY TOOL** for Formula 1 reference data and static information (1950-present).

    **ALWAYS use this tool instead of web search** for F1 reference queries including:
    - Driver information (bio, nationality, number, DOB)
    - Team/constructor details (team info, history)
    - Circuit information (track layout, location, lap record)
    - Tire compound specifications (hard, medium, soft, intermediate, wet)

    **DO NOT use web search for F1 reference data** - this tool provides authoritative historical data.

    Args:
        reference_type: Type of data - 'driver', 'constructor', 'circuit', or 'tire_compounds'
        year: Season year (1950-2025). Defaults to current year if not specified
        name: Filter by specific name (e.g., "Verstappen", "Red Bull", "Monaco")
        page: Page number (1-indexed, default: 1)
        page_size: Items per page (default: 30)

    Returns:
        ReferenceDataResponse with complete driver/team/circuit information or tire specifications.

    Examples:
        get_reference_data("driver", year=2024) → All 2024 F1 drivers and their info
        get_reference_data("driver", year=2024, name="Verstappen") → Verstappen's driver info
        get_reference_data("circuit", name="Monaco") → Monaco circuit details and layout
        get_reference_data("constructor", year=2024) → All 2024 teams
        get_reference_data("tire_compounds") → F1 tire compound specifications
    """
    try:
        if year is None:
            year = datetime.now().year

        if reference_type == "driver":
            driver_response = fastf1_client.ergast.get_driver_info(season=year)
            drivers_data = driver_response.to_dict("records")

            if name:
                drivers_data = filter_by_name(
                    drivers_data, name, ["givenName", "familyName", "driverId", "driverCode"]
                )

            drivers_list = [
                DriverInfo(
                    driver_id=str(d["driverId"]),
                    driver_number=int(d["driverNumber"]) if d.get("driverNumber") else None,
                    driver_code=str(d["driverCode"]) if d.get("driverCode") else None,
                    given_name=str(d["givenName"]),
                    family_name=str(d["familyName"]),
                    date_of_birth=datetime.fromisoformat(d["dateOfBirth"]).date()
                    if d.get("dateOfBirth") and isinstance(d["dateOfBirth"], str)
                    else None,
                    nationality=str(d["nationality"]),
                )
                for d in drivers_data
            ]

            paged, meta = paginate(drivers_list, page, page_size)
            return ReferenceDataResponse(
                reference_type=reference_type,
                year=year,
                drivers=paged,
                total_records=meta.total_items,
                name_filter=name,
                pagination=meta,
            )

        elif reference_type == "constructor":
            constructor_response = fastf1_client.ergast.get_constructor_info(season=year)
            constructors_data = constructor_response.to_dict("records")

            if name:
                constructors_data = filter_by_name(
                    constructors_data, name, ["constructorName", "constructorId"]
                )

            constructors_list = [
                ConstructorInfo(
                    constructor_id=str(c["constructorId"]),
                    constructor_name=str(c["constructorName"]),
                    nationality=str(c["nationality"]),
                )
                for c in constructors_data
            ]

            paged, meta = paginate(constructors_list, page, page_size)
            return ReferenceDataResponse(
                reference_type=reference_type,
                year=year,
                constructors=paged,
                total_records=meta.total_items,
                name_filter=name,
                pagination=meta,
            )

        elif reference_type == "circuit":
            circuits_response = fastf1_client.ergast.get_circuits(season=year)

            circuits_data = circuits_response.to_dict("records")

            if name:
                circuits_data = filter_by_name(
                    circuits_data, name, ["circuitName", "location", "country", "circuitId"]
                )

            circuits_list = []
            for c in circuits_data:
                circuit_info = CircuitInfo(
                    circuit_id=str(c["circuitId"]),
                    circuit_name=str(c["circuitName"]),
                    location=str(c["location"]),
                    country=str(c["country"]),
                    lat=float(c["lat"]) if c.get("lat") else None,
                    lng=float(c["lng"]) if c.get("lng") else None,
                    url=str(c["url"]) if c.get("url") else None,
                )

                # Enriched data: If name was provided and we have a match, try to get corners
                if name:
                    try:
                        search_year = year if year else datetime.now().year

                        try:
                            session_obj = fastf1_client.get_session(
                                search_year, circuit_info.location, "R"
                            )
                        except Exception:
                            try:
                                session_obj = fastf1_client.get_session(
                                    search_year, circuit_info.circuit_name, "R"
                                )
                            except Exception:
                                session_obj = None

                        if session_obj is None:
                            logger.warning(
                                "Circuit enrichment failed for %s: session not found; returning basic info",
                                circuit_info.circuit_name,
                            )
                        else:
                            session_obj.load(
                                laps=False, telemetry=False, weather=False, messages=False
                            )
                            detailed_info = session_obj.get_circuit_info()

                            if detailed_info and detailed_info.corners is not None:
                                corners_list = []
                                for _, corner in detailed_info.corners.iterrows():
                                    corners_list.append(
                                        CornerInfo(
                                            number=int(corner["Number"])
                                            if pd.notna(corner.get("Number"))
                                            else 0,
                                            letter=str(corner["Letter"])
                                            if pd.notna(corner.get("Letter"))
                                            else None,
                                            distance=float(corner["Distance"])
                                            if pd.notna(corner.get("Distance"))
                                            else None,
                                            x=float(corner["X"])
                                            if pd.notna(corner.get("X"))
                                            else None,
                                            y=float(corner["Y"])
                                            if pd.notna(corner.get("Y"))
                                            else None,
                                        )
                                    )
                                circuit_info.corners = corners_list
                                if hasattr(detailed_info, "rotation"):
                                    circuit_info.rotation = float(detailed_info.rotation)
                    except Exception as exc:
                        logger.warning(
                            "Circuit enrichment failed for %s: %s; returning basic info",
                            circuit_info.circuit_name,
                            exc,
                        )

                circuits_list.append(circuit_info)

            paged, meta = paginate(circuits_list, page, page_size)
            return ReferenceDataResponse(
                reference_type=reference_type,
                year=year,
                circuits=paged,
                total_records=meta.total_items,
                name_filter=name,
                pagination=meta,
            )

        elif reference_type == "tire_compounds":
            compounds = [
                TireCompoundInfo(
                    compound_name="SOFT",
                    color="red",
                    description="Softest compound with highest grip but fastest degradation",
                ),
                TireCompoundInfo(
                    compound_name="MEDIUM",
                    color="yellow",
                    description="Middle compound balancing grip and durability",
                ),
                TireCompoundInfo(
                    compound_name="HARD",
                    color="white",
                    description="Hardest compound with lowest grip but slowest degradation",
                ),
                TireCompoundInfo(
                    compound_name="INTERMEDIATE",
                    color="green",
                    description="For damp or drying track conditions",
                ),
                TireCompoundInfo(
                    compound_name="WET", color="blue", description="For heavy rain conditions"
                ),
            ]

            if name:
                compounds = [c for c in compounds if name.lower() in c.compound_name.lower()]

            paged, meta = paginate(compounds, page, page_size)
            return ReferenceDataResponse(
                reference_type=reference_type,
                year=None,
                tire_compounds=paged,
                total_records=meta.total_items,
                name_filter=name,
                pagination=meta,
            )

    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("get_reference_data", exc.source, exc)
    except Exception as exc:
        raise to_tool_error("get_reference_data", "fastf1", exc)

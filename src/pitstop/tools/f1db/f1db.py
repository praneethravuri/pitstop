"""query_f1_database tool — read-only SQL interface for pitstop's owned F1 database."""

import logging
import re

from fastmcp.exceptions import ToolError

from pitstop.clients import get_f1db_client
from pitstop.exceptions import DataSourceError
from pitstop.tools.f1db.models import F1DBResponse
from pitstop.utils import paginate, to_tool_error

logger = logging.getLogger("pitstop.f1db")

_MAX_ROWS = 1000
_ALLOWED_PREFIXES = ("select", "with")
# Strips leading `-- ...` line comments and `/* ... */` block comments so a
# commented SELECT isn't rejected by the prefix check below.
_LEADING_COMMENT_RE = re.compile(r"\A(\s*(--[^\n]*\n|/\*.*?\*/))*", re.DOTALL)


def query_f1_database(
    sql: str,
    page: int = 1,
    page_size: int = 50,
) -> F1DBResponse:
    """
    Execute a read-only SQL query against pitstop's own F1 database.

    This is a SQLite database covering F1 from 1950 to present, seeded from
    F1DB (CC BY 4.0) and extended/self-updated weekly by pitstop. It is a
    normalized relational schema — join across tables/views as needed.

    Key tables/views:
    - race: one row per race weekend. race_data: master per-driver-per-race
      results table that every result view below is derived from.
    - Result views (one row per driver per session): race_result,
      qualifying_result, sprint_race_result, starting_grid_position,
      fastest_lap, pit_stop, free_practice_1_result..free_practice_4_result,
      driver_of_the_day_result.
    - Entities: driver, constructor, circuit, grand_prix, season, chassis,
      engine, engine_manufacturer, tyre_manufacturer, entrant.
    - Junctions: season_entrant_chassis / season_entrant_engine /
      season_entrant_tyre_manufacturer / season_entrant_driver /
      season_entrant_constructor (who ran what, per season),
      constructor_chronology (team lineage / renames over time),
      driver_family_relationship (driver family trees).
    - Pitstop-owned extensions: lap_time (per-lap times for recent races,
      growing weekly), id_map (translates Ergast-style ids used by other
      pitstop tools, e.g. get_results, to this database's f1db ids — join on
      id_map.ergast_id / id_map.f1db_id when combining sources).

    Example queries:
        -- Verstappen family tree
        SELECT d.name, r.other_driver_id, r.type
        FROM driver_family_relationship r
        JOIN driver d ON d.id = r.driver_id
        WHERE r.driver_id = 'max-verstappen';

        -- Aston Martin's team lineage (Jordan -> ... -> Aston Martin)
        SELECT other_constructor_id, year_from, year_to
        FROM constructor_chronology
        WHERE constructor_id = 'aston-martin'
        ORDER BY year_from;

        -- 2026 season roster: entrant/chassis/engine per team
        SELECT sec.entrant_id, sec.constructor_id, sec.chassis_id,
               sec.engine_manufacturer_id
        FROM season_entrant_chassis sec
        WHERE sec.year = 2026;

    Cross-source guidance: use get_telemetry_data for lap-by-lap car
    telemetry, get_live_data for 2023+ live session timing, get_standings
    for current-season championship standings, and get_f1_news for news
    articles — this tool is for structured historical/relational queries.

    IMPORTANT: Only SELECT and WITH (CTE) statements are accepted — no
    INSERT/UPDATE/DELETE/DDL/PRAGMA. The underlying connection is also
    opened read-only, so writes fail even if this guard is bypassed.

    Data attribution: seeded from F1DB (https://github.com/f1db/f1db),
    licensed CC BY 4.0, modified and extended by pitstop.
    """
    stripped = _LEADING_COMMENT_RE.sub("", sql).strip().lower()
    if not any(stripped.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
        raise ToolError(
            "Only SELECT and WITH (read-only) queries are allowed. "
            "INSERT, UPDATE, DELETE, and other write/DDL statements are not permitted."
        )

    try:
        rows = get_f1db_client().query(sql)
    except ToolError:
        raise
    except DataSourceError as exc:
        raise to_tool_error("query_f1_database", "f1db", exc)
    except Exception as exc:
        raise to_tool_error("query_f1_database", "f1db", exc)

    rows = rows[:_MAX_ROWS]

    paged_rows, meta = paginate(rows, page, page_size)

    return F1DBResponse(
        sql=sql,
        rows=paged_rows,
        row_count=len(rows),
        pagination=meta if rows else None,
    )

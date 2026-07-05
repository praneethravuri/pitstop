"""Self-update pitstop's forked f1db database from Jolpica (Ergast-shaped) deltas.

Finds races that have happened but have no ``RACE_RESULT`` rows yet, fetches
results/qualifying/sprint/pitstops/laps/standings from Jolpica, translates
Ergast ids to f1db ids via ``id_map`` (built by ``pitstop-db-seed``), and
writes them in. Idempotent: DELETE+INSERT per (race_id, type), safe to re-run.

Usage:
    uv run pitstop-db-update --db ./f1db.db
    uv run pitstop-db-update --db ./f1db.db --dry-run
    uv run pitstop-db-update --db ./f1db.db --year 2025
    uv run pitstop-db-update --db ./f1db.db --backfill-laps 2023
"""

import argparse
import re
import sqlite3
import time
from datetime import UTC, datetime

from pitstop.db.seed import ENTITIES, PAGE_LIMIT, SLEEP_S, _query, normalize_name

# race_data type discriminators this updater writes.
RACE_RESULT = "RACE_RESULT"
QUALIFYING_RESULT = "QUALIFYING_RESULT"
SPRINT_RACE_RESULT = "SPRINT_RACE_RESULT"
STARTING_GRID_POSITION = "STARTING_GRID_POSITION"
FASTEST_LAP = "FASTEST_LAP"
PIT_STOP = "PIT_STOP"

_LAPS_DOWN_RE = re.compile(r"\+(\d+)\s*Laps?", re.IGNORECASE)


# --------------------------------------------------------------------------
# Small parsing helpers (pure functions)
# --------------------------------------------------------------------------


def _time_to_millis(t: str | None) -> int | None:
    """'1:32:03.275' / '1:23.456' / '22.302' -> milliseconds."""
    if not t:
        return None
    try:
        parts = t.split(":")
        total = float(parts[-1])
        mult = 1
        for p in reversed(parts[:-1]):
            mult *= 60
            total += int(p) * mult
        return round(total * 1000)
    except ValueError:
        return None


def _gap_str(diff_millis: int) -> str:
    return f"+{diff_millis / 1000:.3f}"


def slugify(name: str) -> str:
    """Kebab-case id from a display name, matching f1db's id convention."""
    n = normalize_name(name)
    return re.sub(r"\s+", "-", n)


def _unique_slug(conn: sqlite3.Connection, table: str, base: str) -> str:
    slug = base
    n = 2
    while conn.execute(f"SELECT 1 FROM {table} WHERE id = ?", (slug,)).fetchone():
        slug = f"{base}-{n}"
        n += 1
    return slug


# --------------------------------------------------------------------------
# id_map: load + resolve (creating minimal rows for unknown entities)
# --------------------------------------------------------------------------


def load_id_map(conn: sqlite3.Connection) -> dict[str, dict[str, str]]:
    m: dict[str, dict[str, str]] = {e: {} for e in ENTITIES}
    for row in conn.execute("SELECT entity, ergast_id, f1db_id FROM id_map"):
        m[row["entity"]][row["ergast_id"]] = row["f1db_id"]
    return m


def _country_by_demonym(conn: sqlite3.Connection, nationality: str | None) -> str:
    if nationality:
        row = conn.execute(
            "SELECT id FROM country WHERE lower(demonym) = lower(?)", (nationality,)
        ).fetchone()
        if row:
            return row["id"]
    # ponytail: no fuzzy/manual-override fallback (unlike seed.py's id_overrides.json)
    # for nationalities that don't match a country's demonym exactly. FKs aren't
    # enforced (sqlite3 default), so this dangling id is harmless but wrong;
    # upgrade path: extend id_overrides.json with a nationality->country table.
    return "unknown"


def resolve_driver(
    conn: sqlite3.Connection,
    id_map: dict[str, dict[str, str]],
    d: dict,
    dry_run: bool,
) -> str:
    """Ergast driver dict -> f1db driver id, inserting a minimal row if unknown."""
    ergast_id = d["driverId"]
    known = id_map["driver"].get(ergast_id)
    if known:
        return known

    full = f"{d.get('givenName', '')} {d.get('familyName', '')}".strip()
    f1db_id = _unique_slug(conn, "driver", slugify(full) or ergast_id)
    country_id = _country_by_demonym(conn, d.get("nationality"))
    print(f"[updater] unknown driver ergast_id={ergast_id!r} -> creating {f1db_id!r}")
    # ponytail: gender hardcoded 'male' — Jolpica/Ergast doesn't expose it and every
    # active-era F1 driver is male; revisit if that ever changes.

    if not dry_run:
        conn.execute(
            """
            INSERT INTO driver (
                id, name, first_name, last_name, full_name, abbreviation,
                permanent_number, gender, date_of_birth, place_of_birth,
                country_of_birth_country_id, nationality_country_id,
                best_championship_position, best_starting_grid_position,
                best_race_result, best_sprint_race_result,
                total_championship_wins, total_race_entries, total_race_starts,
                total_race_wins, total_race_laps, total_podiums, total_points,
                total_championship_points, total_pole_positions, total_fastest_laps,
                total_sprint_race_starts, total_sprint_race_wins,
                total_driver_of_the_day, total_grand_slams
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'male', ?, 'Unknown', ?, ?,
                      NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """,
            (
                f1db_id,
                full or ergast_id,
                d.get("givenName", ""),
                d.get("familyName", ""),
                full or ergast_id,
                (d.get("familyName", "") or ergast_id)[:3].upper(),
                d.get("permanentNumber"),
                d.get("dateOfBirth") or "1900-01-01",
                country_id,
                country_id,
            ),
        )
        conn.execute(
            "INSERT INTO id_map (entity, ergast_id, f1db_id) VALUES ('driver', ?, ?)",
            (ergast_id, f1db_id),
        )
    id_map["driver"][ergast_id] = f1db_id
    return f1db_id


def resolve_constructor(
    conn: sqlite3.Connection,
    id_map: dict[str, dict[str, str]],
    c: dict,
    dry_run: bool,
) -> str:
    """Ergast constructor dict -> f1db constructor id, inserting a minimal row if unknown."""
    ergast_id = c["constructorId"]
    known = id_map["constructor"].get(ergast_id)
    if known:
        return known

    name = c.get("name", ergast_id)
    f1db_id = _unique_slug(conn, "constructor", slugify(name) or ergast_id)
    country_id = _country_by_demonym(conn, c.get("nationality"))
    print(f"[updater] unknown constructor ergast_id={ergast_id!r} -> creating {f1db_id!r}")

    if not dry_run:
        conn.execute(
            """
            INSERT INTO constructor (
                id, name, full_name, country_id,
                best_championship_position, best_starting_grid_position,
                best_race_result, best_sprint_race_result,
                total_championship_wins, total_race_entries, total_race_starts,
                total_race_wins, total_1_and_2_finishes, total_race_laps,
                total_podiums, total_podium_races, total_points,
                total_championship_points, total_pole_positions, total_fastest_laps,
                total_sprint_race_starts, total_sprint_race_wins
            ) VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            """,
            (f1db_id, name, name, country_id),
        )
        conn.execute(
            "INSERT INTO id_map (entity, ergast_id, f1db_id) VALUES ('constructor', ?, ?)",
            (ergast_id, f1db_id),
        )
    id_map["constructor"][ergast_id] = f1db_id
    return f1db_id


# --------------------------------------------------------------------------
# engine/tyre manufacturer lookup (NOT NULL columns on race_data)
# --------------------------------------------------------------------------


def engine_tyre_for(conn: sqlite3.Connection, year: int, constructor_id: str) -> tuple | None:
    """(engine_manufacturer_id, tyre_manufacturer_id) for a constructor in a season.

    Tries this season's entrant tables first, then falls back to the
    constructor's most recent race_data row (carry-forward). Returns None if
    truly unknown — caller must skip the race rather than write partial data.
    """
    # ORDER BY keeps the pick deterministic for multi-engine/tyre seasons (rare, historical).
    row = conn.execute(
        "SELECT engine_manufacturer_id FROM season_entrant_engine "
        "WHERE year = ? AND constructor_id = ? ORDER BY engine_manufacturer_id LIMIT 1",
        (year, constructor_id),
    ).fetchone()
    engine = row["engine_manufacturer_id"] if row else None

    row = conn.execute(
        "SELECT tyre_manufacturer_id FROM season_entrant_tyre_manufacturer "
        "WHERE year = ? AND constructor_id = ? ORDER BY tyre_manufacturer_id LIMIT 1",
        (year, constructor_id),
    ).fetchone()
    tyre = row["tyre_manufacturer_id"] if row else None

    if engine is None:
        row = conn.execute(
            "SELECT rd.engine_manufacturer_id FROM race_data rd "
            "JOIN race r ON r.id = rd.race_id "
            "WHERE rd.constructor_id = ? ORDER BY r.date DESC LIMIT 1",
            (constructor_id,),
        ).fetchone()
        engine = row["engine_manufacturer_id"] if row else None
    if tyre is None:
        row = conn.execute(
            "SELECT rd.tyre_manufacturer_id FROM race_data rd "
            "JOIN race r ON r.id = rd.race_id "
            "WHERE rd.constructor_id = ? ORDER BY r.date DESC LIMIT 1",
            (constructor_id,),
        ).fetchone()
        tyre = row["tyre_manufacturer_id"] if row else None

    if engine is None or tyre is None:
        return None
    return engine, tyre


# --------------------------------------------------------------------------
# Jolpica per-race fetch (results/qualifying/sprint are never paginated —
# a race has at most ~26 entries; only pitstops/laps can exceed the page limit)
# --------------------------------------------------------------------------


def _paginate_race(path: str, item_key: str) -> list[dict]:
    items: list[dict] = []
    offset = 0
    while True:
        data = _query(path, limit=PAGE_LIMIT, offset=offset)
        mr = data["MRData"]
        total = int(mr["total"])
        races = mr["RaceTable"]["Races"]
        if races:
            items.extend(races[0][item_key])
        offset += PAGE_LIMIT
        if offset >= total:
            break
        time.sleep(SLEEP_S)
    return items


def fetch_results(year: int, round: int) -> list[dict]:
    data = _query(f"{year}/{round}/results")
    races = data["MRData"]["RaceTable"]["Races"]
    return races[0]["Results"] if races else []


def fetch_qualifying(year: int, round: int) -> list[dict]:
    data = _query(f"{year}/{round}/qualifying")
    races = data["MRData"]["RaceTable"]["Races"]
    return races[0]["QualifyingResults"] if races else []


def fetch_sprint(year: int, round: int) -> list[dict]:
    data = _query(f"{year}/{round}/sprint")
    races = data["MRData"]["RaceTable"]["Races"]
    return races[0]["SprintResults"] if races else []


def fetch_pitstops(year: int, round: int) -> list[dict]:
    return _paginate_race(f"{year}/{round}/pitstops", "PitStops")


def fetch_laps(year: int, round: int) -> list[dict]:
    return _paginate_race(f"{year}/{round}/laps", "Laps")


def fetch_driver_standings(year: int, round: int | None = None) -> list[dict]:
    path = f"{year}/{round}/driverstandings" if round else f"{year}/driverstandings"
    data = _query(path)
    lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    return lists[0]["DriverStandings"] if lists else []


def fetch_constructor_standings(year: int, round: int | None = None) -> list[dict]:
    path = f"{year}/{round}/constructorstandings" if round else f"{year}/constructorstandings"
    data = _query(path)
    lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    return lists[0]["ConstructorStandings"] if lists else []


# --------------------------------------------------------------------------
# gap/interval derivation from classified results (Jolpica gives absolute
# elapsed Time for on-the-lead-lap finishers only; lapped-down cars carry a
# "+N Lap(s)" status instead of a Time)
# --------------------------------------------------------------------------


def _compute_gaps(results: list[dict]) -> dict[str, tuple]:
    """driverId -> (gap, gap_millis, gap_laps, interval, interval_millis)."""
    out: dict[str, tuple] = {}
    leader_millis: int | None = None
    prev_millis: int | None = None
    for r in results:
        driver_id = r["Driver"]["driverId"]
        # Ergast reports Time.millis as an integer string already, for classified
        # finishers on the lead lap only — lapped-down cars have no Time object.
        millis = int(r["Time"]["millis"]) if r.get("Time") and r["Time"].get("millis") else None
        if millis is not None and leader_millis is None:
            leader_millis = millis
        if millis is not None and leader_millis is not None:
            gap_millis = millis - leader_millis
            interval_millis = millis - prev_millis if prev_millis is not None else gap_millis
            out[driver_id] = (
                _gap_str(gap_millis) if gap_millis else None,
                gap_millis or None,
                None,
                _gap_str(interval_millis) if interval_millis else None,
                interval_millis or None,
            )
            prev_millis = millis
        else:
            laps_down = None
            m = _LAPS_DOWN_RE.match(r.get("status", ""))
            if m:
                laps_down = int(m.group(1))
            out[driver_id] = (None, None, laps_down, None, None)
    return out


# --------------------------------------------------------------------------
# race_data row builders — one dict per (race_id, type, position_display_order)
# --------------------------------------------------------------------------


def _base_row(
    race_id: int,
    rtype: str,
    order: int,
    r: dict,
    driver_id: str,
    constructor_id: str,
    engine_id: str,
    tyre_id: str,
    position_number,
    position_text: str,
) -> dict:
    return {
        "race_id": race_id,
        "type": rtype,
        "position_display_order": order,
        "position_number": position_number,
        "position_text": position_text,
        "driver_number": str(r.get("number", "")),
        "driver_id": driver_id,
        "constructor_id": constructor_id,
        "engine_manufacturer_id": engine_id,
        "tyre_manufacturer_id": tyre_id,
    }


def build_race_result_rows(
    race_id: int,
    results: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    qual_position_by_driver: dict[str, int],
    pit_stop_counts: dict[str, int],
    dry_run: bool,
) -> list[dict]:
    gaps = _compute_gaps(results)
    rows = []
    for order, r in enumerate(results, start=1):
        driver_id = resolve_driver(conn, id_map, r["Driver"], dry_run)
        constructor_id = resolve_constructor(conn, id_map, r["Constructor"], dry_run)
        engine_id, tyre_id = et_by_constructor[constructor_id]
        position_number = int(r["position"]) if r["position"].isdigit() else None
        grid = int(r["grid"]) if str(r.get("grid", "")).isdigit() else None
        gap, gap_millis, gap_laps, interval, interval_millis = gaps.get(
            r["Driver"]["driverId"], (None, None, None, None, None)
        )
        fl = r.get("FastestLap") or {}
        row = _base_row(
            race_id,
            RACE_RESULT,
            order,
            r,
            driver_id,
            constructor_id,
            engine_id,
            tyre_id,
            position_number,
            r["positionText"],
        )
        qual_pos = qual_position_by_driver.get(r["Driver"]["driverId"])
        row.update(
            {
                "shared_car": 0,
                "laps": int(r["laps"]),
                "time": r.get("Time", {}).get("time"),
                "time_millis": int(r["Time"]["millis"]) if r.get("Time") else None,
                "time_penalty": None,
                "time_penalty_millis": None,
                "gap": gap,
                "gap_millis": gap_millis,
                "gap_laps": gap_laps,
                "interval": interval,
                "interval_millis": interval_millis,
                "reason_retired": r["status"] if r["status"] != "Finished" else None,
                "points": float(r["points"]),
                "pole_position": 1
                if grid == 1
                else 0,  # ponytail: approximated from grid, see report
                "qualification_position_number": qual_pos,
                "qualification_position_text": str(qual_pos) if qual_pos else None,
                # grid 0 = pit-lane start: f1db stores NULL position with "PL" text
                # (a literal 0 would corrupt MIN(position_number) aggregates).
                "grid_position_number": grid or None,
                "grid_position_text": "PL"
                if grid == 0
                else (str(grid) if grid is not None else None),
                "positions_gained": (grid - position_number) if grid and position_number else None,
                "pit_stops": pit_stop_counts.get(r["Driver"]["driverId"], 0),
                "fastest_lap": 1 if fl.get("rank") == "1" else 0,
                "driver_of_the_day": None,
                "grand_slam": None,
            }
        )
        rows.append(row)
    return rows


def build_qualifying_rows(
    race_id: int,
    quali: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    dry_run: bool,
) -> list[dict]:
    rows = []
    for order, r in enumerate(quali, start=1):
        driver_id = resolve_driver(conn, id_map, r["Driver"], dry_run)
        constructor_id = resolve_constructor(conn, id_map, r["Constructor"], dry_run)
        engine_id, tyre_id = et_by_constructor[constructor_id]
        q1, q2, q3 = r.get("Q1"), r.get("Q2"), r.get("Q3")
        best = q3 or q2 or q1
        row = _base_row(
            race_id,
            QUALIFYING_RESULT,
            order,
            r,
            driver_id,
            constructor_id,
            engine_id,
            tyre_id,
            int(r["position"]),
            str(r["position"]),
        )
        row.update(
            {
                "time": best,
                "time_millis": _time_to_millis(best),
                "q1": q1,
                "q1_millis": _time_to_millis(q1),
                "q2": q2,
                "q2_millis": _time_to_millis(q2),
                "q3": q3,
                "q3_millis": _time_to_millis(q3),
                "gap": None,
                "gap_millis": None,
                "interval": None,
                "interval_millis": None,
                "laps": None,
            }
        )
        rows.append(row)
    return rows


def build_sprint_rows(
    race_id: int,
    sprint: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    qual_position_by_driver: dict[str, int],
    dry_run: bool,
) -> list[dict]:
    gaps = _compute_gaps(sprint)
    rows = []
    for order, r in enumerate(sprint, start=1):
        driver_id = resolve_driver(conn, id_map, r["Driver"], dry_run)
        constructor_id = resolve_constructor(conn, id_map, r["Constructor"], dry_run)
        engine_id, tyre_id = et_by_constructor[constructor_id]
        position_number = int(r["position"]) if r["position"].isdigit() else None
        grid = int(r["grid"]) if str(r.get("grid", "")).isdigit() else None
        gap, gap_millis, gap_laps, interval, interval_millis = gaps.get(
            r["Driver"]["driverId"], (None, None, None, None, None)
        )
        qual_pos = qual_position_by_driver.get(r["Driver"]["driverId"])
        row = _base_row(
            race_id,
            SPRINT_RACE_RESULT,
            order,
            r,
            driver_id,
            constructor_id,
            engine_id,
            tyre_id,
            position_number,
            r["positionText"],
        )
        row.update(
            {
                "laps": int(r["laps"]),
                "time": r.get("Time", {}).get("time"),
                "time_millis": int(r["Time"]["millis"]) if r.get("Time") else None,
                "time_penalty": None,
                "time_penalty_millis": None,
                "gap": gap,
                "gap_millis": gap_millis,
                "gap_laps": gap_laps,
                "interval": interval,
                "interval_millis": interval_millis,
                "reason_retired": r["status"] if r["status"] != "Finished" else None,
                "points": float(r["points"]),
                "qualification_position_number": qual_pos,
                "qualification_position_text": str(qual_pos) if qual_pos else None,
                # grid 0 = pit-lane start: f1db stores NULL position with "PL" text
                # (a literal 0 would corrupt MIN(position_number) aggregates).
                "grid_position_number": grid or None,
                "grid_position_text": "PL"
                if grid == 0
                else (str(grid) if grid is not None else None),
                "positions_gained": (grid - position_number) if grid and position_number else None,
            }
        )
        rows.append(row)
    return rows


def build_grid_rows(
    race_id: int,
    results: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    qual_position_by_driver: dict[str, int],
    dry_run: bool,
) -> list[dict]:
    """STARTING_GRID_POSITION rows derived from the race results' grid field (req #3)."""
    with_grid = [r for r in results if str(r.get("grid", "")).isdigit()]
    with_grid.sort(key=lambda r: int(r["grid"]) if int(r["grid"]) > 0 else 999)
    rows = []
    for order, r in enumerate(with_grid, start=1):
        driver_id = resolve_driver(conn, id_map, r["Driver"], dry_run)
        constructor_id = resolve_constructor(conn, id_map, r["Constructor"], dry_run)
        engine_id, tyre_id = et_by_constructor[constructor_id]
        grid = int(r["grid"])
        qual_pos = qual_position_by_driver.get(r["Driver"]["driverId"])
        row = _base_row(
            race_id,
            STARTING_GRID_POSITION,
            order,
            r,
            driver_id,
            constructor_id,
            engine_id,
            tyre_id,
            grid or None,  # pit-lane start (grid 0) -> NULL position, "PL" text
            "PL" if grid == 0 else str(grid),
        )
        row.update(
            {
                "qualification_position_number": qual_pos,
                "qualification_position_text": str(qual_pos) if qual_pos else None,
                "grid_penalty": None,
                "grid_penalty_positions": None,
                "time": None,
                "time_millis": None,
            }
        )
        rows.append(row)
    return rows


def build_fastest_lap_rows(
    race_id: int,
    results: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    dry_run: bool,
) -> list[dict]:
    """FASTEST_LAP rows derived from the race results' FastestLap field (req #3)."""
    with_fl = [r for r in results if r.get("FastestLap")]
    with_fl.sort(key=lambda r: int(r["FastestLap"].get("rank", 999)))
    rows = []
    for order, r in enumerate(with_fl, start=1):
        driver_id = resolve_driver(conn, id_map, r["Driver"], dry_run)
        constructor_id = resolve_constructor(conn, id_map, r["Constructor"], dry_run)
        engine_id, tyre_id = et_by_constructor[constructor_id]
        fl = r["FastestLap"]
        t = fl.get("Time", {}).get("time")
        row = _base_row(
            race_id,
            FASTEST_LAP,
            order,
            r,
            driver_id,
            constructor_id,
            engine_id,
            tyre_id,
            order,
            str(order),
        )
        row.update(
            {
                "lap": int(fl["lap"]) if fl.get("lap") else None,
                "time": t,
                "time_millis": _time_to_millis(t),
                "gap": None,
                "gap_millis": None,
                "interval": None,
                "interval_millis": None,
            }
        )
        rows.append(row)
    return rows


def build_pitstop_rows(
    race_id: int,
    pitstops: list[dict],
    id_map: dict,
    conn: sqlite3.Connection,
    et_by_constructor: dict[str, tuple],
    driver_context: dict[str, dict],
    dry_run: bool,
) -> list[dict]:
    """PIT_STOP rows. Jolpica's /pitstops entries only carry driverId (no
    constructor/number) — backfilled from the race results we already fetched."""
    # f1db orders PIT_STOP rows chronologically; Jolpica's "time" is the wall-clock
    # HH:MM:SS of the stop, which sorts lexicographically. (lap, stop) breaks ties.
    ordered = sorted(pitstops, key=lambda p: (p.get("time") or "", int(p["lap"]), int(p["stop"])))
    rows = []
    for order, p in enumerate(ordered, start=1):
        ergast_driver_id = p["driverId"]
        ctx = driver_context.get(ergast_driver_id)
        if ctx is None:
            print(f"[updater] pit stop for unknown driver {ergast_driver_id!r} in race skipped")
            continue
        driver_id, constructor_id, number = ctx["driver_id"], ctx["constructor_id"], ctx["number"]
        engine_id, tyre_id = et_by_constructor[constructor_id]
        row = {
            "race_id": race_id,
            "type": PIT_STOP,
            "position_display_order": order,
            "position_number": None,
            "position_text": str(p["stop"]),
            "driver_number": number,
            "driver_id": driver_id,
            "constructor_id": constructor_id,
            "engine_manufacturer_id": engine_id,
            "tyre_manufacturer_id": tyre_id,
            "stop": int(p["stop"]),
            "lap": int(p["lap"]),
            "time": p.get("duration"),
            "time_millis": _time_to_millis(p.get("duration")),
        }
        rows.append(row)
    return rows


_COLUMN_PREFIX = {
    RACE_RESULT: "race_",
    SPRINT_RACE_RESULT: "race_",
    QUALIFYING_RESULT: "qualifying_",
    STARTING_GRID_POSITION: "starting_grid_position_",
    FASTEST_LAP: "fastest_lap_",
    PIT_STOP: "pit_stop_",
}
_UNPREFIXED = {
    "race_id",
    "type",
    "position_display_order",
    "position_number",
    "position_text",
    "driver_number",
    "driver_id",
    "constructor_id",
    "engine_manufacturer_id",
    "tyre_manufacturer_id",
}


def _to_race_data_columns(rtype: str, row: dict) -> dict:
    """Map a builder's view-column-named dict to the underlying race_data columns."""
    prefix = _COLUMN_PREFIX[rtype]
    out = {}
    for k, v in row.items():
        out[k if k in _UNPREFIXED else f"{prefix}{k}"] = v
    return out


def write_race_data(conn: sqlite3.Connection, race_id: int, rtype: str, rows: list[dict]) -> None:
    conn.execute("DELETE FROM race_data WHERE race_id = ? AND type = ?", (race_id, rtype))
    if not rows:
        return
    mapped = [_to_race_data_columns(rtype, r) for r in rows]
    cols = list(mapped[0].keys())
    placeholders = ", ".join("?" for _ in cols)
    conn.executemany(
        f"INSERT INTO race_data ({', '.join(cols)}) VALUES ({placeholders})",
        [tuple(m[c] for c in cols) for m in mapped],
    )


# --------------------------------------------------------------------------
# standings
# --------------------------------------------------------------------------


def write_race_standings(
    conn: sqlite3.Connection,
    race_id: int,
    year: int,
    round: int,
    id_map: dict,
    dry_run: bool,
) -> None:
    driver_standings = fetch_driver_standings(year, round)
    constructor_standings = fetch_constructor_standings(year, round)

    conn.execute("DELETE FROM race_driver_standing WHERE race_id = ?", (race_id,))
    for order, s in enumerate(driver_standings, start=1):
        driver_id = resolve_driver(conn, id_map, s["Driver"], dry_run)
        conn.execute(
            "INSERT INTO race_driver_standing "
            "(race_id, position_display_order, position_number, position_text, "
            "driver_id, points, positions_gained, championship_won) "
            "VALUES (?, ?, ?, ?, ?, ?, NULL, 0)",
            (race_id, order, int(s["position"]), s["positionText"], driver_id, float(s["points"])),
        )

    conn.execute("DELETE FROM race_constructor_standing WHERE race_id = ?", (race_id,))
    for order, s in enumerate(constructor_standings, start=1):
        constructor_id = resolve_constructor(conn, id_map, s["Constructor"], dry_run)
        et = engine_tyre_for(conn, year, constructor_id)
        if et is None:  # same gate as ingest_race: never write a made-up manufacturer id
            print(
                f"[updater] {year}: unknown engine manufacturer for constructor "
                f"{constructor_id!r}; skipping its standing row"
            )
            continue
        engine_id = et[0]
        conn.execute(
            "INSERT INTO race_constructor_standing "
            "(race_id, position_display_order, position_number, position_text, "
            "constructor_id, engine_manufacturer_id, points, positions_gained, championship_won) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, NULL, 0)",
            (
                race_id,
                order,
                int(s["position"]),
                s["positionText"],
                constructor_id,
                engine_id,
                float(s["points"]),
            ),
        )
    # ponytail: championship_won always 0 and positions_gained always NULL — both
    # need "is this the season's last race" / prior-round comparison logic that
    # isn't worth it for a weekly sync. Upgrade path: compare round to the max
    # round in `race` for that year, and diff position vs the previous round.


def refresh_season_standings(
    conn: sqlite3.Connection, year: int, id_map: dict, dry_run: bool
) -> None:
    driver_standings = fetch_driver_standings(year)
    constructor_standings = fetch_constructor_standings(year)

    conn.execute("DELETE FROM season_driver_standing WHERE year = ?", (year,))
    for order, s in enumerate(driver_standings, start=1):
        driver_id = resolve_driver(conn, id_map, s["Driver"], dry_run)
        conn.execute(
            "INSERT INTO season_driver_standing "
            "(year, position_display_order, position_number, position_text, driver_id, points, "
            "championship_won) VALUES (?, ?, ?, ?, ?, ?, 0)",
            (year, order, int(s["position"]), s["positionText"], driver_id, float(s["points"])),
        )

    conn.execute("DELETE FROM season_constructor_standing WHERE year = ?", (year,))
    for order, s in enumerate(constructor_standings, start=1):
        constructor_id = resolve_constructor(conn, id_map, s["Constructor"], dry_run)
        et = engine_tyre_for(conn, year, constructor_id)
        if et is None:  # same gate as ingest_race: never write a made-up manufacturer id
            print(
                f"[updater] {year}: unknown engine manufacturer for constructor "
                f"{constructor_id!r}; skipping its standing row"
            )
            continue
        engine_id = et[0]
        conn.execute(
            "INSERT INTO season_constructor_standing "
            "(year, position_display_order, position_number, position_text, constructor_id, "
            "engine_manufacturer_id, points, championship_won) VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
            (
                year,
                order,
                int(s["position"]),
                s["positionText"],
                constructor_id,
                engine_id,
                float(s["points"]),
            ),
        )
    # ponytail: championship_won always 0 — see write_race_standings note above.


# --------------------------------------------------------------------------
# lap_time
# --------------------------------------------------------------------------


def write_lap_time(
    conn: sqlite3.Connection, race_id: int, year: int, round: int, id_map: dict
) -> int:
    laps = fetch_laps(year, round)
    conn.execute("DELETE FROM lap_time WHERE race_id = ?", (race_id,))
    n = 0
    for lap in laps:
        lap_num = int(lap["number"])
        for timing in lap.get("Timings", []):
            ergast_driver_id = timing["driverId"]
            driver_id = id_map["driver"].get(ergast_driver_id)
            if driver_id is None:
                continue  # unknown drivers are created during results ingest, which runs first
            conn.execute(
                "INSERT OR REPLACE INTO lap_time (race_id, driver_id, lap, position, time, time_millis) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    race_id,
                    driver_id,
                    lap_num,
                    int(timing["position"]) if timing.get("position") else None,
                    timing.get("time"),
                    _time_to_millis(timing.get("time")),
                ),
            )
            n += 1
    return n


# --------------------------------------------------------------------------
# aggregate recompute (driver/constructor denormalized totals — req #7)
# --------------------------------------------------------------------------
#
# ponytail: only the columns cleanly derivable as a single SQL aggregate over
# race_data (+ season standings for best_championship_position) are recomputed.
# Skipped (left as whatever the seed/previous run had, not recomputed here):
#   driver:      total_race_starts (needs DNS/DNQ status parsing, not just
#                entries), total_championship_wins, total_championship_points
#                (need championship_won, which we don't derive — see above),
#                total_driver_of_the_day, total_grand_slams (no data source).
#   constructor: total_race_starts, total_1_and_2_finishes (needs a self-join
#                per race), total_championship_wins, total_championship_points.
# Upgrade path: implement championship_won properly (compare round to season's
# last round) and these all fall out cheaply.


def recompute_driver_aggregates(conn: sqlite3.Connection, driver_ids: set[str]) -> None:
    for driver_id in driver_ids:
        row = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT') AS entries,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND position_number = 1) AS wins,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND position_number <= 3) AS podiums,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND race_pole_position = 1) AS poles,
                COUNT(*) FILTER (WHERE type = 'FASTEST_LAP' AND position_display_order = 1) AS fastest_laps,
                SUM(CASE WHEN type = 'RACE_RESULT' THEN race_points ELSE 0 END) AS points,
                SUM(CASE WHEN type = 'RACE_RESULT' THEN race_laps ELSE 0 END) AS total_race_laps,
                MIN(CASE WHEN type = 'RACE_RESULT' THEN position_number END) AS best_result,
                MIN(CASE WHEN type = 'STARTING_GRID_POSITION' THEN position_number END) AS best_grid,
                COUNT(*) FILTER (WHERE type = 'SPRINT_RACE_RESULT') AS sprint_starts,
                COUNT(*) FILTER (WHERE type = 'SPRINT_RACE_RESULT' AND position_number = 1) AS sprint_wins,
                MIN(CASE WHEN type = 'SPRINT_RACE_RESULT' THEN position_number END) AS best_sprint
            FROM race_data WHERE driver_id = ?
            """,
            (driver_id,),
        ).fetchone()
        best_champ = conn.execute(
            "SELECT MIN(position_number) FROM season_driver_standing WHERE driver_id = ?",
            (driver_id,),
        ).fetchone()[0]
        conn.execute(
            """
            UPDATE driver SET
                total_race_entries = ?, total_race_wins = ?, total_podiums = ?,
                total_pole_positions = ?, total_fastest_laps = ?, total_points = ?,
                total_race_laps = ?, best_race_result = ?, best_starting_grid_position = ?,
                total_sprint_race_starts = ?, total_sprint_race_wins = ?,
                best_sprint_race_result = ?, best_championship_position = ?
            WHERE id = ?
            """,
            (
                row["entries"],
                row["wins"],
                row["podiums"],
                row["poles"],
                row["fastest_laps"],
                row["points"] or 0,
                row["total_race_laps"] or 0,
                row["best_result"],
                row["best_grid"],
                row["sprint_starts"],
                row["sprint_wins"],
                row["best_sprint"],
                best_champ,
                driver_id,
            ),
        )


def recompute_constructor_aggregates(conn: sqlite3.Connection, constructor_ids: set[str]) -> None:
    for constructor_id in constructor_ids:
        row = conn.execute(
            """
            SELECT
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT') AS entries,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND position_number = 1) AS wins,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND position_number <= 3) AS podiums,
                COUNT(DISTINCT CASE WHEN type = 'RACE_RESULT' AND position_number <= 3
                    THEN race_id END) AS podium_races,
                COUNT(*) FILTER (WHERE type = 'RACE_RESULT' AND race_pole_position = 1) AS poles,
                COUNT(*) FILTER (WHERE type = 'FASTEST_LAP' AND position_display_order = 1) AS fastest_laps,
                SUM(CASE WHEN type = 'RACE_RESULT' THEN race_points ELSE 0 END) AS points,
                SUM(CASE WHEN type = 'RACE_RESULT' THEN race_laps ELSE 0 END) AS total_race_laps,
                MIN(CASE WHEN type = 'RACE_RESULT' THEN position_number END) AS best_result,
                MIN(CASE WHEN type = 'STARTING_GRID_POSITION' THEN position_number END) AS best_grid,
                COUNT(*) FILTER (WHERE type = 'SPRINT_RACE_RESULT') AS sprint_starts,
                COUNT(*) FILTER (WHERE type = 'SPRINT_RACE_RESULT' AND position_number = 1) AS sprint_wins,
                MIN(CASE WHEN type = 'SPRINT_RACE_RESULT' THEN position_number END) AS best_sprint
            FROM race_data WHERE constructor_id = ?
            """,
            (constructor_id,),
        ).fetchone()
        best_champ = conn.execute(
            "SELECT MIN(position_number) FROM season_constructor_standing WHERE constructor_id = ?",
            (constructor_id,),
        ).fetchone()[0]
        conn.execute(
            """
            UPDATE constructor SET
                total_race_entries = ?, total_race_wins = ?, total_podiums = ?,
                total_podium_races = ?, total_pole_positions = ?, total_fastest_laps = ?,
                total_points = ?, total_race_laps = ?, best_race_result = ?,
                best_starting_grid_position = ?, total_sprint_race_starts = ?,
                total_sprint_race_wins = ?, best_sprint_race_result = ?,
                best_championship_position = ?
            WHERE id = ?
            """,
            (
                row["entries"],
                row["wins"],
                row["podiums"],
                row["podium_races"],
                row["poles"],
                row["fastest_laps"],
                row["points"] or 0,
                row["total_race_laps"] or 0,
                row["best_result"],
                row["best_grid"],
                row["sprint_starts"],
                row["sprint_wins"],
                row["best_sprint"],
                best_champ,
                constructor_id,
            ),
        )


# --------------------------------------------------------------------------
# target-race detection + single-race ingest
# --------------------------------------------------------------------------


def target_races(conn: sqlite3.Connection, year: int) -> list[sqlite3.Row]:
    """race rows with date < today, year >= --year, and no RACE_RESULT yet (req #1)."""
    today = datetime.now(UTC).date().isoformat()
    return conn.execute(
        """
        SELECT id, year, round FROM race
        WHERE date < ? AND year >= ?
          AND NOT EXISTS (
              SELECT 1 FROM race_data WHERE race_data.race_id = race.id
              AND race_data.type = 'RACE_RESULT'
          )
        ORDER BY year, round
        """,
        (today, year),
    ).fetchall()


def ingest_race(
    conn: sqlite3.Connection, race_row: sqlite3.Row, id_map: dict, dry_run: bool
) -> dict[str, int] | None:
    """Fetch + write everything for one race. Returns row counts, or None if skipped."""
    race_id, year, round = race_row["id"], race_row["year"], race_row["round"]

    results = fetch_results(year, round)
    if not results:
        print(f"[updater] {year}/{round}: no results yet from Jolpica, skipping")
        return None
    time.sleep(SLEEP_S)
    quali = fetch_qualifying(year, round)
    time.sleep(SLEEP_S)
    pitstops = fetch_pitstops(year, round)
    time.sleep(SLEEP_S)
    sprint = fetch_sprint(year, round)
    time.sleep(SLEEP_S)

    # Resolve every constructor's engine/tyre BEFORE writing any race_data (req #2:
    # "if still unknown, skip that race with a clear error message"). This does
    # create/persist unknown driver/constructor + id_map rows for the race's
    # entrants even if the race then gets skipped below — creating an identity
    # row isn't "partial race data" and it saves re-deriving it next run.
    constructor_ids = set()
    for r in results + quali + sprint:
        constructor_ids.add(resolve_constructor(conn, id_map, r["Constructor"], dry_run))
    et_by_constructor = {}
    for cid in constructor_ids:
        et = engine_tyre_for(conn, year, cid)
        if et is None:
            print(
                f"[updater] {year}/{round}: unknown engine/tyre manufacturer for "
                f"constructor {cid!r}; skipping this race entirely"
            )
            return None
        et_by_constructor[cid] = et

    qual_position_by_driver = {
        r["Driver"]["driverId"]: int(r["position"]) for r in quali if r.get("position")
    }
    pit_stop_counts: dict[str, int] = {}
    for p in pitstops:
        pit_stop_counts[p["driverId"]] = pit_stop_counts.get(p["driverId"], 0) + 1
    driver_context = {
        r["Driver"]["driverId"]: {
            "driver_id": resolve_driver(conn, id_map, r["Driver"], dry_run),
            "constructor_id": resolve_constructor(conn, id_map, r["Constructor"], dry_run),
            "number": str(r.get("number", "")),
        }
        for r in results
    }

    race_rows = build_race_result_rows(
        race_id,
        results,
        id_map,
        conn,
        et_by_constructor,
        qual_position_by_driver,
        pit_stop_counts,
        dry_run,
    )
    grid_rows = build_grid_rows(
        race_id, results, id_map, conn, et_by_constructor, qual_position_by_driver, dry_run
    )
    fl_rows = build_fastest_lap_rows(race_id, results, id_map, conn, et_by_constructor, dry_run)
    quali_rows = build_qualifying_rows(race_id, quali, id_map, conn, et_by_constructor, dry_run)
    pit_rows = build_pitstop_rows(
        race_id, pitstops, id_map, conn, et_by_constructor, driver_context, dry_run
    )
    sprint_rows = (
        build_sprint_rows(
            race_id, sprint, id_map, conn, et_by_constructor, qual_position_by_driver, dry_run
        )
        if sprint
        else []
    )

    counts = {
        "race_result": len(race_rows),
        "starting_grid_position": len(grid_rows),
        "fastest_lap": len(fl_rows),
        "qualifying_result": len(quali_rows),
        "pit_stop": len(pit_rows),
        "sprint_race_result": len(sprint_rows),
    }

    if dry_run:
        return counts

    write_race_data(conn, race_id, RACE_RESULT, race_rows)
    write_race_data(conn, race_id, STARTING_GRID_POSITION, grid_rows)
    write_race_data(conn, race_id, FASTEST_LAP, fl_rows)
    write_race_data(conn, race_id, QUALIFYING_RESULT, quali_rows)
    write_race_data(conn, race_id, PIT_STOP, pit_rows)
    if sprint_rows:
        write_race_data(conn, race_id, SPRINT_RACE_RESULT, sprint_rows)

    write_race_standings(conn, race_id, year, round, id_map, dry_run)
    time.sleep(SLEEP_S)
    counts["lap_time"] = write_lap_time(conn, race_id, year, round, id_map)
    conn.commit()
    return counts


# --------------------------------------------------------------------------
# season bootstrap (req #8) — best-effort: only handles races at circuits
# f1db already knows about (the overwhelmingly common case: next year's
# calendar reuses existing tracks). A genuinely new circuit is logged and
# skipped — building circuit/circuit_layout from Ergast's Location data alone
# isn't enough to fill f1db's circuit_type/direction/turns/layout columns.
# --------------------------------------------------------------------------


def bootstrap_season(conn: sqlite3.Connection, year: int, id_map: dict, dry_run: bool) -> None:
    data = _query(f"{year}/races")
    races = data["MRData"]["RaceTable"]["Races"]
    if not races:
        return

    existing_rounds = {
        r["round"] for r in conn.execute("SELECT round FROM race WHERE year = ?", (year,))
    }
    new = [r for r in races if int(r["round"]) not in existing_rounds]
    if not new:
        return

    if not dry_run:
        conn.execute("INSERT OR IGNORE INTO season (year) VALUES (?)", (year,))

    for r in new:
        ergast_circuit_id = r["Circuit"]["circuitId"]
        circuit_id = id_map["circuit"].get(ergast_circuit_id)
        if circuit_id is None:
            print(
                f"[updater] {year}/{r['round']}: new circuit {ergast_circuit_id!r} not in "
                "id_map — add it to id_overrides.json / seed's id_map manually, skipping this race"
            )
            continue

        template = conn.execute(
            "SELECT * FROM race WHERE circuit_id = ? ORDER BY date DESC LIMIT 1", (circuit_id,)
        ).fetchone()
        if template is None:
            print(
                f"[updater] {year}/{r['round']}: circuit {circuit_id!r} has no prior race to "
                "template from, skipping"
            )
            continue

        grand_prix_id = template["grand_prix_id"]
        print(
            f"[updater] {year}/{r['round']}: bootstrapping new race at {circuit_id!r} "
            f"from {template['year']}/{template['round']} template (verify manually)"
        )
        if dry_run:
            continue

        conn.execute(
            """
            INSERT INTO race (
                id, year, round, date, time, grand_prix_id, official_name, qualifying_format,
                sprint_qualifying_format, circuit_id, circuit_layout_id, circuit_type, direction,
                course_length, turns, laps, distance, scheduled_laps, scheduled_distance,
                drivers_championship_decider, constructors_championship_decider
            )
            SELECT
                (SELECT COALESCE(MAX(id), 0) + 1 FROM race),
                ?, ?, ?, ?, ?, ?, qualifying_format, sprint_qualifying_format, circuit_id,
                circuit_layout_id, circuit_type, direction, course_length, turns, laps, distance,
                scheduled_laps, scheduled_distance, 0, 0
            FROM race WHERE id = ?
            """,
            (
                year,
                int(r["round"]),
                r["date"],
                r.get("time"),
                grand_prix_id,
                r.get("raceName", template["official_name"]),
                template["id"],
            ),
        )
        # carry forward season_entrant_* from the prior year for this circuit's usual entrants
        prior_year = year - 1
        for tbl in ("season_entrant_engine", "season_entrant_tyre_manufacturer"):
            n = conn.execute(f"SELECT COUNT(*) FROM {tbl} WHERE year = ?", (year,)).fetchone()[0]
            if n == 0:
                conn.execute(
                    f"INSERT INTO {tbl} SELECT ? AS year, entrant_id, constructor_id, "
                    f"engine_manufacturer_id, "
                    + ("engine_id" if tbl == "season_entrant_engine" else "tyre_manufacturer_id")
                    + f" FROM {tbl} WHERE year = ?",
                    (year, prior_year),
                )
                print(
                    f"[updater] {year}: carried forward {tbl} from {prior_year} (verify manually)"
                )
    conn.commit()


# --------------------------------------------------------------------------
# backfill mode
# --------------------------------------------------------------------------


def backfill_laps(conn: sqlite3.Connection, year: int, id_map: dict, dry_run: bool) -> None:
    races = conn.execute(
        "SELECT id, round FROM race WHERE year = ? AND date < ? ORDER BY round",
        (year, datetime.now(UTC).date().isoformat()),
    ).fetchall()
    for race_row in races:
        has_laps = conn.execute(
            "SELECT 1 FROM lap_time WHERE race_id = ? LIMIT 1", (race_row["id"],)
        ).fetchone()
        if has_laps:
            continue
        if dry_run:
            print(f"[updater] would backfill lap_time for {year}/{race_row['round']}")
            continue
        n = write_lap_time(conn, race_row["id"], year, race_row["round"], id_map)
        print(f"[updater] backfilled {n} lap_time rows for {year}/{race_row['round']}")
        conn.commit()
        time.sleep(SLEEP_S)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Update pitstop's f1db-derived database.")
    parser.add_argument("--db", required=True, help="Path to the pitstop f1db.db")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print planned changes, write nothing"
    )
    parser.add_argument("--year", type=int, default=None, help="Earliest season year to update")
    parser.add_argument(
        "--backfill-laps",
        type=int,
        default=None,
        metavar="YEAR",
        help="Alternate mode: ingest lap_time for every race of YEAR lacking rows",
    )
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    id_map = load_id_map(conn)

    if args.backfill_laps is not None:
        backfill_laps(conn, args.backfill_laps, id_map, args.dry_run)
        conn.close()
        return

    year = args.year or datetime.now(UTC).year

    bootstrap_season(conn, year, id_map, args.dry_run)

    races = target_races(conn, year)
    print(f"[updater] {len(races)} target race(s) for year >= {year}")

    touched_drivers: set[str] = set()
    touched_constructors: set[str] = set()
    affected_years: set[int] = set()

    for race_row in races:
        time.sleep(SLEEP_S)  # pace consecutive races on backlog runs
        counts = ingest_race(conn, race_row, id_map, args.dry_run)
        if counts is None:
            continue
        print(f"[updater] {race_row['year']}/{race_row['round']}: {counts}")
        if not args.dry_run:
            affected_years.add(race_row["year"])
            for row in conn.execute(
                "SELECT DISTINCT driver_id, constructor_id FROM race_data WHERE race_id = ?",
                (race_row["id"],),
            ):
                touched_drivers.add(row["driver_id"])
                touched_constructors.add(row["constructor_id"])

    if args.dry_run:
        conn.close()
        return

    for y in affected_years:
        time.sleep(SLEEP_S)
        refresh_season_standings(conn, y, id_map, args.dry_run)
        conn.commit()

    recompute_driver_aggregates(conn, touched_drivers)
    recompute_constructor_aggregates(conn, touched_constructors)
    conn.commit()

    today = datetime.now(UTC).date().isoformat()
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_updated', ?)", (today,))
    conn.commit()
    conn.close()
    print(f"[updater] done. last_updated={today}")


if __name__ == "__main__":
    main()

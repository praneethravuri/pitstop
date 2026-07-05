"""Offline unit tests for pitstop.db.updater — no live network calls.

Fixture DDL for race/race_data/driver/constructor/*standing/season_entrant_*
is copied (trimmed of indexes) from the real seeded db's schema, per the
task brief, so INSERT column lists line up with production.
"""

import sqlite3

import pytest

import pitstop.db.seed as seed_mod
import pitstop.db.updater as updater
from pitstop.db.seed import ensure_schema
from pitstop.db.updater import ingest_race, load_id_map, target_races

# --------------------------------------------------------------------------
# fixture DB
# --------------------------------------------------------------------------

_DDL = """
CREATE TABLE "race"
( "id" INTEGER NOT NULL PRIMARY KEY
, "year" INTEGER NOT NULL
, "round" INTEGER NOT NULL
, "date" DATE NOT NULL
, "grand_prix_id" VARCHAR(100)
, "official_name" VARCHAR(100)
, "circuit_id" VARCHAR(100)
);

CREATE TABLE "race_data"
( "race_id" INTEGER NOT NULL
, "type" VARCHAR(50) NOT NULL
, "position_display_order" INTEGER NOT NULL
, "position_number" INTEGER
, "position_text" VARCHAR(4) NOT NULL
, "driver_number" VARCHAR(3) NOT NULL
, "driver_id" VARCHAR(100) NOT NULL
, "constructor_id" VARCHAR(100) NOT NULL
, "engine_manufacturer_id" VARCHAR(100) NOT NULL
, "tyre_manufacturer_id" VARCHAR(100) NOT NULL
, "practice_time" VARCHAR(20)
, "practice_time_millis" INTEGER
, "qualifying_time" VARCHAR(20)
, "qualifying_time_millis" INTEGER
, "qualifying_q1" VARCHAR(20)
, "qualifying_q1_millis" INTEGER
, "qualifying_q2" VARCHAR(20)
, "qualifying_q2_millis" INTEGER
, "qualifying_q3" VARCHAR(20)
, "qualifying_q3_millis" INTEGER
, "qualifying_gap" VARCHAR(20)
, "qualifying_gap_millis" INTEGER
, "qualifying_interval" VARCHAR(20)
, "qualifying_interval_millis" INTEGER
, "qualifying_laps" INTEGER
, "starting_grid_position_qualification_position_number" INTEGER
, "starting_grid_position_qualification_position_text" VARCHAR(4)
, "starting_grid_position_grid_penalty" VARCHAR(20)
, "starting_grid_position_grid_penalty_positions" INTEGER
, "starting_grid_position_time" VARCHAR(20)
, "starting_grid_position_time_millis" INTEGER
, "race_shared_car" BOOLEAN
, "race_laps" INTEGER
, "race_time" VARCHAR(20)
, "race_time_millis" INTEGER
, "race_time_penalty" VARCHAR(20)
, "race_time_penalty_millis" INTEGER
, "race_gap" VARCHAR(20)
, "race_gap_millis" INTEGER
, "race_gap_laps" INTEGER
, "race_interval" VARCHAR(20)
, "race_interval_millis" INTEGER
, "race_reason_retired" VARCHAR(100)
, "race_points" DECIMAL(8,2)
, "race_pole_position" BOOLEAN
, "race_qualification_position_number" INTEGER
, "race_qualification_position_text" VARCHAR(4)
, "race_grid_position_number" INTEGER
, "race_grid_position_text" VARCHAR(2)
, "race_positions_gained" INTEGER
, "race_pit_stops" INTEGER
, "race_fastest_lap" BOOLEAN
, "race_driver_of_the_day" BOOLEAN
, "race_grand_slam" BOOLEAN
, "fastest_lap_lap" INTEGER
, "fastest_lap_time" VARCHAR(20)
, "fastest_lap_time_millis" INTEGER
, "fastest_lap_gap" VARCHAR(20)
, "fastest_lap_gap_millis" INTEGER
, "fastest_lap_interval" VARCHAR(20)
, "fastest_lap_interval_millis" INTEGER
, "pit_stop_stop" INTEGER
, "pit_stop_lap" INTEGER
, "pit_stop_time" VARCHAR(20)
, "pit_stop_time_millis" INTEGER
, "driver_of_the_day_percentage" DECIMAL(5,2)
, PRIMARY KEY ("race_id", "type", "position_display_order")
);

CREATE TABLE "race_driver_standing"
( "race_id" INTEGER NOT NULL
, "position_display_order" INTEGER NOT NULL
, "position_number" INTEGER
, "position_text" VARCHAR(4) NOT NULL
, "driver_id" VARCHAR(100) NOT NULL
, "points" DECIMAL(8,2) NOT NULL
, "positions_gained" INTEGER
, "championship_won" BOOLEAN NOT NULL
, PRIMARY KEY ("race_id", "position_display_order")
);

CREATE TABLE "race_constructor_standing"
( "race_id" INTEGER NOT NULL
, "position_display_order" INTEGER NOT NULL
, "position_number" INTEGER
, "position_text" VARCHAR(4) NOT NULL
, "constructor_id" VARCHAR(100) NOT NULL
, "engine_manufacturer_id" VARCHAR(100) NOT NULL
, "points" DECIMAL(8,2) NOT NULL
, "positions_gained" INTEGER
, "championship_won" BOOLEAN NOT NULL
, PRIMARY KEY ("race_id", "position_display_order")
);

CREATE TABLE "season_driver_standing"
( "year" INTEGER NOT NULL
, "position_display_order" INTEGER NOT NULL
, "position_number" INTEGER
, "position_text" VARCHAR(4) NOT NULL
, "driver_id" VARCHAR(100) NOT NULL
, "points" DECIMAL(8,2) NOT NULL
, "championship_won" BOOLEAN NOT NULL
, PRIMARY KEY ("year", "position_display_order")
);

CREATE TABLE "season_constructor_standing"
( "year" INTEGER NOT NULL
, "position_display_order" INTEGER NOT NULL
, "position_number" INTEGER
, "position_text" VARCHAR(4) NOT NULL
, "constructor_id" VARCHAR(100) NOT NULL
, "engine_manufacturer_id" VARCHAR(100) NOT NULL
, "points" DECIMAL(8,2) NOT NULL
, "championship_won" BOOLEAN NOT NULL
, PRIMARY KEY ("year", "position_display_order")
);

CREATE TABLE "season_entrant_engine"
( "year" INTEGER NOT NULL
, "entrant_id" VARCHAR(100) NOT NULL
, "constructor_id" VARCHAR(100) NOT NULL
, "engine_manufacturer_id" VARCHAR(100) NOT NULL
, "engine_id" VARCHAR(100) NOT NULL
, PRIMARY KEY ("year", "entrant_id", "constructor_id", "engine_manufacturer_id", "engine_id")
);

CREATE TABLE "season_entrant_tyre_manufacturer"
( "year" INTEGER NOT NULL
, "entrant_id" VARCHAR(100) NOT NULL
, "constructor_id" VARCHAR(100) NOT NULL
, "engine_manufacturer_id" VARCHAR(100) NOT NULL
, "tyre_manufacturer_id" VARCHAR(100) NOT NULL
, PRIMARY KEY ("year", "entrant_id", "constructor_id", "engine_manufacturer_id", "tyre_manufacturer_id")
);

CREATE TABLE "driver"
( "id" VARCHAR(100) NOT NULL PRIMARY KEY
, "name" VARCHAR(100) NOT NULL
, "first_name" VARCHAR(100) NOT NULL
, "last_name" VARCHAR(100) NOT NULL
, "full_name" VARCHAR(100) NOT NULL
, "abbreviation" VARCHAR(3) NOT NULL
, "permanent_number" VARCHAR(2)
, "gender" VARCHAR(6) NOT NULL
, "date_of_birth" DATE NOT NULL
, "place_of_birth" VARCHAR(100) NOT NULL
, "country_of_birth_country_id" VARCHAR(100) NOT NULL
, "nationality_country_id" VARCHAR(100) NOT NULL
, "best_championship_position" INTEGER
, "best_starting_grid_position" INTEGER
, "best_race_result" INTEGER
, "best_sprint_race_result" INTEGER
, "total_championship_wins" INTEGER NOT NULL
, "total_race_entries" INTEGER NOT NULL
, "total_race_starts" INTEGER NOT NULL
, "total_race_wins" INTEGER NOT NULL
, "total_race_laps" INTEGER NOT NULL
, "total_podiums" INTEGER NOT NULL
, "total_points" DECIMAL(8,2) NOT NULL
, "total_championship_points" DECIMAL(8,2) NOT NULL
, "total_pole_positions" INTEGER NOT NULL
, "total_fastest_laps" INTEGER NOT NULL
, "total_sprint_race_starts" INTEGER NOT NULL
, "total_sprint_race_wins" INTEGER NOT NULL
, "total_driver_of_the_day" INTEGER NOT NULL
, "total_grand_slams" INTEGER NOT NULL
);

CREATE TABLE "constructor"
( "id" VARCHAR(100) NOT NULL PRIMARY KEY
, "name" VARCHAR(100) NOT NULL
, "full_name" VARCHAR(100) NOT NULL
, "country_id" VARCHAR(100) NOT NULL
, "best_championship_position" INTEGER
, "best_starting_grid_position" INTEGER
, "best_race_result" INTEGER
, "best_sprint_race_result" INTEGER
, "total_championship_wins" INTEGER NOT NULL
, "total_race_entries" INTEGER NOT NULL
, "total_race_starts" INTEGER NOT NULL
, "total_race_wins" INTEGER NOT NULL
, "total_1_and_2_finishes" INTEGER NOT NULL
, "total_race_laps" INTEGER NOT NULL
, "total_podiums" INTEGER NOT NULL
, "total_podium_races" INTEGER NOT NULL
, "total_points" DECIMAL(8,2) NOT NULL
, "total_championship_points" DECIMAL(8,2) NOT NULL
, "total_pole_positions" INTEGER NOT NULL
, "total_fastest_laps" INTEGER NOT NULL
, "total_sprint_race_starts" INTEGER NOT NULL
, "total_sprint_race_wins" INTEGER NOT NULL
);

CREATE TABLE "country"
( "id" VARCHAR(100) NOT NULL PRIMARY KEY
, "name" VARCHAR(100) NOT NULL
, "demonym" VARCHAR(100)
);
"""


def _make_db(tmp_path) -> sqlite3.Connection:
    conn = sqlite3.connect(tmp_path / "f1db.db")
    conn.row_factory = sqlite3.Row
    conn.executescript(_DDL)
    ensure_schema(conn)  # meta, id_map, lap_time — reuse seed.py, don't duplicate

    conn.execute(
        "INSERT INTO driver (id, name, first_name, last_name, full_name, abbreviation, "
        "gender, date_of_birth, place_of_birth, country_of_birth_country_id, "
        "nationality_country_id, total_championship_wins, total_race_entries, "
        "total_race_starts, total_race_wins, total_race_laps, total_podiums, total_points, "
        "total_championship_points, total_pole_positions, total_fastest_laps, "
        "total_sprint_race_starts, total_sprint_race_wins, total_driver_of_the_day, "
        "total_grand_slams) VALUES "
        "('max-verstappen', 'Max Verstappen', 'Max', 'Verstappen', 'Max Verstappen', 'VER', "
        "'male', '1997-09-30', 'Hasselt', 'netherlands', 'netherlands', 0,0,0,0,0,0,0,0,0,0,0,0,0,0)"
    )
    conn.execute(
        "INSERT INTO constructor (id, name, full_name, country_id, total_championship_wins, "
        "total_race_entries, total_race_starts, total_race_wins, total_1_and_2_finishes, "
        "total_race_laps, total_podiums, total_podium_races, total_points, "
        "total_championship_points, total_pole_positions, total_fastest_laps, "
        "total_sprint_race_starts, total_sprint_race_wins) VALUES "
        "('red-bull', 'Red Bull', 'Red Bull Racing', 'austria', 0,0,0,0,0,0,0,0,0,0,0,0,0,0)"
    )
    conn.executemany(
        "INSERT INTO country (id, name, demonym) VALUES (?, ?, ?)",
        [
            ("netherlands", "Netherlands", "Dutch"),
            ("mexico", "Mexico", "Mexican"),
            ("austria", "Austria", "Austrian"),
        ],
    )
    conn.executemany(
        "INSERT INTO id_map (entity, ergast_id, f1db_id) VALUES (?, ?, ?)",
        [
            ("driver", "max_verstappen", "max-verstappen"),
            ("constructor", "red_bull", "red-bull"),
        ],
    )
    conn.execute(
        "INSERT INTO season_entrant_engine (year, entrant_id, constructor_id, "
        "engine_manufacturer_id, engine_id) VALUES (2020, 'red-bull', 'red-bull', "
        "'honda-rbpt', 'honda-rbpt-engine')"
    )
    conn.execute(
        "INSERT INTO season_entrant_tyre_manufacturer (year, entrant_id, constructor_id, "
        "engine_manufacturer_id, tyre_manufacturer_id) VALUES (2020, 'red-bull', 'red-bull', "
        "'honda-rbpt', 'pirelli')"
    )
    conn.commit()
    return conn


# --------------------------------------------------------------------------
# canned Jolpica payloads for year=2020, round=1
# --------------------------------------------------------------------------

_DRIVER_VER = {
    "driverId": "max_verstappen",
    "givenName": "Max",
    "familyName": "Verstappen",
    "dateOfBirth": "1997-09-30",
    "nationality": "Dutch",
}
_DRIVER_NEW = {
    "driverId": "new_driver_x",
    "givenName": "New",
    "familyName": "Driverx",
    "dateOfBirth": "1999-05-05",
    "nationality": "Mexican",
}
_CONSTRUCTOR_RB = {"constructorId": "red_bull", "name": "Red Bull", "nationality": "Austrian"}

_RESULTS = [
    {
        "number": "1",
        "position": "1",
        "positionText": "1",
        "points": "25",
        "Driver": _DRIVER_VER,
        "Constructor": _CONSTRUCTOR_RB,
        "grid": "1",
        "laps": "50",
        "status": "Finished",
        "Time": {"millis": "5000000", "time": "1:23:20.000"},
        "FastestLap": {"rank": "1", "lap": "44", "Time": {"time": "1:30.000"}},
    },
    {
        "number": "22",
        "position": "2",
        "positionText": "2",
        "points": "18",
        "Driver": _DRIVER_NEW,
        "Constructor": _CONSTRUCTOR_RB,
        "grid": "2",
        "laps": "50",
        "status": "Finished",
        "Time": {"millis": "5010000", "time": "1:23:30.000"},
        "FastestLap": {"rank": "2", "lap": "45", "Time": {"time": "1:31.000"}},
    },
]

_QUALI = [
    {
        "number": "1",
        "position": "1",
        "Driver": _DRIVER_VER,
        "Constructor": _CONSTRUCTOR_RB,
        "Q1": "1:29.000",
        "Q2": "1:28.000",
        "Q3": "1:27.000",
    },
    {
        "number": "22",
        "position": "2",
        "Driver": _DRIVER_NEW,
        "Constructor": _CONSTRUCTOR_RB,
        "Q1": "1:29.500",
        "Q2": "1:28.500",
        "Q3": "1:27.500",
    },
]

_PITSTOPS = [
    {
        "driverId": "max_verstappen",
        "lap": "10",
        "stop": "1",
        "time": "14:20:01",
        "duration": "22.302",
    },
]

_LAPS = [
    {
        "number": "1",
        "Timings": [
            {"driverId": "max_verstappen", "position": "1", "time": "1:35.000"},
            {"driverId": "new_driver_x", "position": "2", "time": "1:35.500"},
        ],
    },
    {
        "number": "2",
        "Timings": [
            {"driverId": "max_verstappen", "position": "1", "time": "1:34.900"},
            {"driverId": "new_driver_x", "position": "2", "time": "1:35.400"},
        ],
    },
]

_DRIVER_STANDINGS = [
    {"position": "1", "positionText": "1", "points": "25", "Driver": _DRIVER_VER},
    {"position": "2", "positionText": "2", "points": "18", "Driver": _DRIVER_NEW},
]
_CONSTRUCTOR_STANDINGS = [
    {"position": "1", "positionText": "1", "points": "43", "Constructor": _CONSTRUCTOR_RB},
]


def _fake_query_factory():
    def fake_query(path: str, **params) -> dict:
        if path == "2020/1/results":
            return {"MRData": {"total": "2", "RaceTable": {"Races": [{"Results": _RESULTS}]}}}
        if path == "2020/1/qualifying":
            return {
                "MRData": {"total": "2", "RaceTable": {"Races": [{"QualifyingResults": _QUALI}]}}
            }
        if path == "2020/1/sprint":
            return {"MRData": {"total": "0", "RaceTable": {"Races": []}}}
        if path == "2020/1/pitstops":
            return {
                "MRData": {
                    "total": str(len(_PITSTOPS)),
                    "RaceTable": {"Races": [{"PitStops": _PITSTOPS}]},
                }
            }
        if path == "2020/1/laps":
            return {"MRData": {"total": str(len(_LAPS)), "RaceTable": {"Races": [{"Laps": _LAPS}]}}}
        if path in ("2020/1/driverstandings", "2020/driverstandings"):
            return {
                "MRData": {
                    "StandingsTable": {"StandingsLists": [{"DriverStandings": _DRIVER_STANDINGS}]}
                }
            }
        if path in ("2020/1/constructorstandings", "2020/constructorstandings"):
            return {
                "MRData": {
                    "StandingsTable": {
                        "StandingsLists": [{"ConstructorStandings": _CONSTRUCTOR_STANDINGS}]
                    }
                }
            }
        raise AssertionError(f"unexpected path in test: {path}")

    return fake_query


@pytest.fixture(autouse=True)
def _no_sleep_no_network(monkeypatch):
    monkeypatch.setattr(updater.time, "sleep", lambda _s: None)
    monkeypatch.setattr(seed_mod.time, "sleep", lambda _s: None)
    monkeypatch.setattr(seed_mod.jolpica_client, "query", _fake_query_factory())


# --------------------------------------------------------------------------
# target-race detection
# --------------------------------------------------------------------------


def test_target_races_detects_only_unplayed_past_races_in_year_scope(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute(
        "INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')"
    )  # no RACE_RESULT yet -> target
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (2, 2020, 2, '2020-03-15')")
    conn.execute(
        "INSERT INTO race_data (race_id, type, position_display_order, position_text, "
        "driver_number, driver_id, constructor_id, engine_manufacturer_id, tyre_manufacturer_id) "
        "VALUES (2, 'RACE_RESULT', 1, '1', '1', 'max-verstappen', 'red-bull', 'honda-rbpt', 'pirelli')"
    )  # already has a result -> not a target
    conn.execute(
        "INSERT INTO race (id, year, round, date) VALUES (3, 2019, 1, '2019-03-01')"
    )  # earlier than --year -> out of scope
    conn.execute(
        "INSERT INTO race (id, year, round, date) VALUES (4, 2020, 3, '2099-01-01')"
    )  # in the future -> not yet a target
    conn.commit()

    races = target_races(conn, year=2020)
    assert [r["id"] for r in races] == [1]


# --------------------------------------------------------------------------
# one-race ingest: all race_data types + standings + lap_time
# --------------------------------------------------------------------------


def test_ingest_race_populates_all_types_standings_and_lap_time(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()
    id_map = load_id_map(conn)
    race_row = conn.execute("SELECT * FROM race WHERE id = 1").fetchone()

    counts = ingest_race(conn, race_row, id_map, dry_run=False)

    assert counts == {
        "race_result": 2,
        "starting_grid_position": 2,
        "fastest_lap": 2,
        "qualifying_result": 2,
        "pit_stop": 1,
        "sprint_race_result": 0,
        "lap_time": 4,
    }
    types = {
        r["type"] for r in conn.execute("SELECT DISTINCT type FROM race_data WHERE race_id = 1")
    }
    assert types == {
        "RACE_RESULT",
        "STARTING_GRID_POSITION",
        "FASTEST_LAP",
        "QUALIFYING_RESULT",
        "PIT_STOP",
    }
    assert (
        conn.execute("SELECT COUNT(*) FROM race_driver_standing WHERE race_id = 1").fetchone()[0]
        == 2
    )
    assert (
        conn.execute("SELECT COUNT(*) FROM race_constructor_standing WHERE race_id = 1").fetchone()[
            0
        ]
        == 1
    )
    assert conn.execute("SELECT COUNT(*) FROM lap_time WHERE race_id = 1").fetchone()[0] == 4


# --------------------------------------------------------------------------
# idempotency: run twice -> identical counts, no duplicate rows
# --------------------------------------------------------------------------


def test_ingest_race_is_idempotent(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()
    id_map = load_id_map(conn)
    race_row = conn.execute("SELECT * FROM race WHERE id = 1").fetchone()

    first = ingest_race(conn, race_row, id_map, dry_run=False)
    second = ingest_race(conn, race_row, load_id_map(conn), dry_run=False)

    assert first == second
    assert (
        conn.execute("SELECT COUNT(*) FROM race_data WHERE race_id = 1").fetchone()[0]
        == 2 + 2 + 2 + 2 + 1  # race_result + grid + fastest_lap + qualifying + pit_stop
    )
    assert (
        conn.execute("SELECT COUNT(*) FROM driver WHERE id LIKE 'new-driverx%'").fetchone()[0] == 1
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM id_map WHERE entity = 'driver' AND ergast_id = 'new_driver_x'"
        ).fetchone()[0]
        == 1
    )


# --------------------------------------------------------------------------
# unknown driver -> new driver row + id_map row
# --------------------------------------------------------------------------


def test_ingest_race_creates_unknown_driver_and_id_map_row(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()
    id_map = load_id_map(conn)
    race_row = conn.execute("SELECT * FROM race WHERE id = 1").fetchone()

    ingest_race(conn, race_row, id_map, dry_run=False)

    new_id = id_map["driver"]["new_driver_x"]
    row = conn.execute("SELECT * FROM driver WHERE id = ?", (new_id,)).fetchone()
    assert row is not None
    assert row["full_name"] == "New Driverx"
    assert row["nationality_country_id"] == "mexico"
    mapped = conn.execute(
        "SELECT f1db_id FROM id_map WHERE entity = 'driver' AND ergast_id = 'new_driver_x'"
    ).fetchone()
    assert mapped["f1db_id"] == new_id


# --------------------------------------------------------------------------
# dry-run writes nothing
# --------------------------------------------------------------------------


def test_ingest_race_dry_run_writes_nothing(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()
    id_map = load_id_map(conn)
    race_row = conn.execute("SELECT * FROM race WHERE id = 1").fetchone()

    counts = ingest_race(conn, race_row, id_map, dry_run=True)

    assert counts["race_result"] == 2
    assert conn.execute("SELECT COUNT(*) FROM race_data").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM race_driver_standing").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM lap_time").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM driver").fetchone()[0] == 1  # only the fixture row
    assert conn.execute("SELECT COUNT(*) FROM id_map").fetchone()[0] == 2  # only the fixture rows


def test_backfill_laps_dry_run_writes_nothing(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()

    updater.backfill_laps(conn, 2020, load_id_map(conn), dry_run=True)

    assert conn.execute("SELECT COUNT(*) FROM lap_time").fetchone()[0] == 0


# --------------------------------------------------------------------------
# empty StandingsLists (BLOCKER 1): a Jolpica 200 with no standings yet must
# never wipe rows a previous run already wrote.
# --------------------------------------------------------------------------


def test_empty_standings_payload_preserves_existing_rows(tmp_path, monkeypatch):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.execute(
        "INSERT INTO race_driver_standing (race_id, position_display_order, position_number, "
        "position_text, driver_id, points, positions_gained, championship_won) "
        "VALUES (1, 1, 1, '1', 'max-verstappen', 25.0, NULL, 0)"
    )
    conn.execute(
        "INSERT INTO race_constructor_standing (race_id, position_display_order, "
        "position_number, position_text, constructor_id, engine_manufacturer_id, points, "
        "positions_gained, championship_won) VALUES (1, 1, 1, '1', 'red-bull', 'honda-rbpt', "
        "43.0, NULL, 0)"
    )
    conn.execute(
        "INSERT INTO season_driver_standing (year, position_display_order, position_number, "
        "position_text, driver_id, points, championship_won) "
        "VALUES (2020, 1, 1, '1', 'max-verstappen', 25.0, 0)"
    )
    conn.execute(
        "INSERT INTO season_constructor_standing (year, position_display_order, "
        "position_number, position_text, constructor_id, engine_manufacturer_id, points, "
        "championship_won) VALUES (2020, 1, 1, '1', 'red-bull', 'honda-rbpt', 43.0, 0)"
    )
    conn.commit()
    id_map = load_id_map(conn)
    monkeypatch.setattr(updater, "fetch_driver_standings", lambda year, round=None: [])
    monkeypatch.setattr(updater, "fetch_constructor_standings", lambda year, round=None: [])

    updater.write_race_standings(conn, race_id=1, year=2020, round=1, id_map=id_map, dry_run=False)
    updater.refresh_season_standings(conn, year=2020, id_map=id_map, dry_run=False)

    assert (
        conn.execute("SELECT COUNT(*) FROM race_driver_standing WHERE race_id = 1").fetchone()[0]
        == 1
    )
    assert (
        conn.execute("SELECT COUNT(*) FROM race_constructor_standing WHERE race_id = 1").fetchone()[
            0
        ]
        == 1
    )
    assert (
        conn.execute("SELECT COUNT(*) FROM season_driver_standing WHERE year = 2020").fetchone()[0]
        == 1
    )
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM season_constructor_standing WHERE year = 2020"
        ).fetchone()[0]
        == 1
    )


# --------------------------------------------------------------------------
# pit-lane start (grid "0") -> NULL positions, "PL" text, aggregates unharmed
# --------------------------------------------------------------------------


def test_pit_lane_start_writes_null_position_not_zero(tmp_path):
    conn = _make_db(tmp_path)
    conn.execute("INSERT INTO race (id, year, round, date) VALUES (1, 2020, 1, '2020-03-01')")
    conn.commit()
    id_map = load_id_map(conn)
    et = {"red-bull": ("honda-rbpt", "pirelli")}
    results = [
        {
            "number": "1",
            "position": "1",
            "positionText": "1",
            "points": "25",
            "Driver": _DRIVER_VER,
            "Constructor": _CONSTRUCTOR_RB,
            "grid": "3",
            "laps": "50",
            "status": "Finished",
            "Time": {"millis": "5000000", "time": "1:23:20.000"},
        },
        {
            "number": "22",
            "position": "2",
            "positionText": "2",
            "points": "18",
            "Driver": _DRIVER_NEW,
            "Constructor": _CONSTRUCTOR_RB,
            "grid": "0",  # pit-lane start
            "laps": "50",
            "status": "Finished",
            "Time": {"millis": "5010000", "time": "1:23:30.000"},
        },
    ]

    race_rows = updater.build_race_result_rows(1, results, id_map, conn, et, {}, {}, dry_run=False)
    grid_rows = updater.build_grid_rows(1, results, id_map, conn, et, {}, dry_run=False)
    sprint_rows = updater.build_sprint_rows(1, results, id_map, conn, et, {}, dry_run=False)
    updater.write_race_data(conn, 1, updater.STARTING_GRID_POSITION, grid_rows)

    pl_race = next(r for r in race_rows if r["driver_number"] == "22")
    assert pl_race["grid_position_number"] is None
    assert pl_race["grid_position_text"] == "PL"
    pl_sprint = next(r for r in sprint_rows if r["driver_number"] == "22")
    assert pl_sprint["grid_position_number"] is None
    pl_grid = next(r for r in grid_rows if r["driver_number"] == "22")
    assert pl_grid["position_number"] is None
    assert pl_grid["position_text"] == "PL"
    # a 0 here would have poisoned MIN(position_number) -> best_starting_grid_position
    assert (
        conn.execute(
            "SELECT MIN(position_number) FROM race_data WHERE type = 'STARTING_GRID_POSITION'"
        ).fetchone()[0]
        == 3
    )

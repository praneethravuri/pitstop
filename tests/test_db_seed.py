"""Offline unit tests for pitstop.db.seed — no live network calls."""

import json
import sqlite3

import pytest

import pitstop.db.seed as seed_mod
from pitstop.db.seed import (
    build_id_map,
    copy_source,
    ensure_schema,
    load_overrides,
    match_by_name,
    match_driver,
    normalize_name,
    write_id_map,
    write_meta,
)
from pitstop.exceptions import DataSourceError

# --------------------------------------------------------------------------
# normalize_name
# --------------------------------------------------------------------------


def test_normalize_name():
    assert normalize_name("Sérgio Pérez") == "sergio perez"
    assert normalize_name("Max VERSTAPPEN") == "max verstappen"
    assert normalize_name("Jean-Éric  Vergne") == "jean eric vergne"


# --------------------------------------------------------------------------
# match_driver
# --------------------------------------------------------------------------

DRIVER_DOB_MAP = {
    "1997-09-30": [
        {
            "id": "max-verstappen",
            "name": "Max Verstappen",
            "full_name": "Max Emilian Verstappen",
            "first_name": "Max",
            "last_name": "Verstappen",
        }
    ],
    "1990-01-26": [
        {
            "id": "sergio-perez",
            "name": "Sergio Pérez",
            "full_name": "Sergio Michel Pérez Mendoza",
            "first_name": "Sergio",
            "last_name": "Pérez",
        }
    ],
    "2000-01-01": [
        {
            "id": "john-smith",
            "name": "John Smith",
            "full_name": "John Michael Smith",
            "first_name": "John",
            "last_name": "Smith",
        },
        {
            "id": "john-jones",
            "name": "John Jones",
            "full_name": "John Michael Jones",
            "first_name": "John",
            "last_name": "Jones",
        },
    ],
}


def test_match_driver_exact_via_name_field():
    jd = {
        "driverId": "max_verstappen",
        "givenName": "Max",
        "familyName": "Verstappen",
        "dateOfBirth": "1997-09-30",
    }
    assert match_driver(jd, DRIVER_DOB_MAP) == "max-verstappen"


def test_match_driver_accent_insensitive():
    jd = {
        "driverId": "perez",
        "givenName": "Sergio",
        "familyName": "Perez",
        "dateOfBirth": "1990-01-26",
    }
    assert match_driver(jd, DRIVER_DOB_MAP) == "sergio-perez"


def test_match_driver_dob_matches_multiple_but_family_unique():
    jd = {
        "driverId": "j_smith",
        "givenName": "Jon",
        "familyName": "Smith",
        "dateOfBirth": "2000-01-01",
    }
    assert match_driver(jd, DRIVER_DOB_MAP) == "john-smith"


def test_match_driver_dob_matches_multiple_family_ambiguous():
    jd = {
        "driverId": "j_unknown",
        "givenName": "Jon",
        "familyName": "Doe",
        "dateOfBirth": "2000-01-01",
    }
    assert match_driver(jd, DRIVER_DOB_MAP) is None


def test_match_driver_no_dob_candidates():
    jd = {
        "driverId": "nobody",
        "givenName": "No",
        "familyName": "Body",
        "dateOfBirth": "1900-01-01",
    }
    assert match_driver(jd, DRIVER_DOB_MAP) is None


# --------------------------------------------------------------------------
# match_by_name
# --------------------------------------------------------------------------

CONSTRUCTOR_ROWS = [
    {"id": "mercedes", "name": "Mercedes", "full_name": "Mercedes-AMG Petronas F1 Team"},
    {"id": "ferrari", "name": "Ferrari", "full_name": "Scuderia Ferrari"},
]


def test_match_by_name_exact_name_field():
    assert match_by_name("Mercedes", CONSTRUCTOR_ROWS) == "mercedes"


def test_match_by_name_exact_full_name_field():
    assert match_by_name("Scuderia Ferrari", CONSTRUCTOR_ROWS) == "ferrari"


def test_match_by_name_no_match():
    assert match_by_name("Some Unknown Team", CONSTRUCTOR_ROWS) is None


def test_match_by_name_ambiguous_returns_none():
    rows = [
        {"id": "a", "name": "Team X", "full_name": "Team X Racing"},
        {"id": "b", "name": "Team X", "full_name": "Other"},
    ]
    assert match_by_name("Team X", rows) is None


# --------------------------------------------------------------------------
# _query 429 backoff
# --------------------------------------------------------------------------


def test_query_retries_on_429_then_succeeds(monkeypatch):
    monkeypatch.setattr(seed_mod.time, "sleep", lambda _s: None)
    calls = {"n": 0}

    def fake_query(path, **params):
        calls["n"] += 1
        if calls["n"] < 3:
            raise DataSourceError("jolpica", path, "429 Too Many Requests")
        return {"ok": True}

    monkeypatch.setattr(seed_mod.jolpica_client, "query", fake_query)
    assert seed_mod._query("drivers") == {"ok": True}
    assert calls["n"] == 3


def test_query_reraises_non_429_immediately(monkeypatch):
    monkeypatch.setattr(seed_mod.time, "sleep", lambda _s: (_ for _ in ()).throw(AssertionError()))

    def fake_query(path, **params):
        raise DataSourceError("jolpica", path, "404 Not Found")

    monkeypatch.setattr(seed_mod.jolpica_client, "query", fake_query)
    with pytest.raises(DataSourceError):
        seed_mod._query("drivers")


def test_query_reraises_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr(seed_mod.time, "sleep", lambda _s: None)

    def fake_query(path, **params):
        raise DataSourceError("jolpica", path, "429 Too Many Requests")

    monkeypatch.setattr(seed_mod.jolpica_client, "query", fake_query)
    with pytest.raises(DataSourceError):
        seed_mod._query("drivers")


# --------------------------------------------------------------------------
# copy_source
# --------------------------------------------------------------------------


def test_copy_source_same_path_is_a_noop(tmp_path):
    """Re-running with --source and --out pointing at the same already-seeded db
    must not crash (shutil.copy raises SameFileError on identical paths)."""
    db_path = tmp_path / "f1db.db"
    db_path.write_bytes(b"not a real sqlite file, just proving no copy is attempted")
    seeded_from = copy_source(str(db_path), db_path)
    assert seeded_from == "local"
    assert db_path.read_bytes() == b"not a real sqlite file, just proving no copy is attempted"


def test_copy_source_plain_file_copies(tmp_path):
    src = tmp_path / "source.db"
    src.write_bytes(b"sqlite-bytes")
    out = tmp_path / "out.db"
    seeded_from = copy_source(str(src), out)
    assert seeded_from == "local"
    assert out.read_bytes() == b"sqlite-bytes"


# --------------------------------------------------------------------------
# schema DDL
# --------------------------------------------------------------------------


def _make_f1db_conn(tmp_path):
    conn = sqlite3.connect(tmp_path / "f1db.db")
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE driver (id TEXT PRIMARY KEY, name TEXT, full_name TEXT, "
        "first_name TEXT, last_name TEXT, date_of_birth TEXT)"
    )
    conn.execute("CREATE TABLE constructor (id TEXT PRIMARY KEY, name TEXT, full_name TEXT)")
    conn.execute("CREATE TABLE circuit (id TEXT PRIMARY KEY, name TEXT, full_name TEXT)")
    conn.executemany(
        "INSERT INTO driver VALUES (?, ?, ?, ?, ?, ?)",
        [
            (
                "max-verstappen",
                "Max Verstappen",
                "Max Emilian Verstappen",
                "Max",
                "Verstappen",
                "1997-09-30",
            ),
            (
                "sergio-perez",
                "Sergio Pérez",
                "Sergio Michel Pérez Mendoza",
                "Sergio",
                "Pérez",
                "1990-01-26",
            ),
            (
                "lewis-hamilton",
                "Lewis Hamilton",
                "Lewis Carl Davidson Hamilton",
                "Lewis",
                "Hamilton",
                "1985-01-07",
            ),
        ],
    )
    conn.execute(
        "INSERT INTO constructor VALUES ('mercedes', 'Mercedes', 'Mercedes-AMG Petronas F1 Team')"
    )
    conn.execute("INSERT INTO circuit VALUES ('monza', 'Monza', 'Autodromo Nazionale Monza')")
    conn.commit()
    return conn


def test_ensure_schema_creates_tables(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"meta", "id_map", "lap_time"} <= tables


def test_ensure_schema_idempotent(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)
    ensure_schema(conn)  # must not raise
    tables = [r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert tables.count("meta") == 1


def test_write_meta_preserves_seeded_at_across_reruns(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)
    write_meta(conn, "v2026.1.1")
    first_seeded_at = conn.execute("SELECT value FROM meta WHERE key='seeded_at'").fetchone()[0]

    write_meta(conn, "v2026.2.2")
    seeded_from = conn.execute("SELECT value FROM meta WHERE key='seeded_from'").fetchone()[0]
    seeded_at = conn.execute("SELECT value FROM meta WHERE key='seeded_at'").fetchone()[0]
    schema_version = conn.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0]

    assert seeded_from == "v2026.1.1"  # not overwritten by second call
    assert seeded_at == first_seeded_at
    assert schema_version == "1"


# --------------------------------------------------------------------------
# build_id_map + overrides
# --------------------------------------------------------------------------


def test_build_id_map_resolves_via_matching_and_overrides(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)

    jolpica_drivers = [
        {
            "driverId": "max_verstappen",
            "givenName": "Max",
            "familyName": "Verstappen",
            "dateOfBirth": "1997-09-30",
        },
        {
            "driverId": "perez",
            "givenName": "Sergio",
            "familyName": "Perez",
            "dateOfBirth": "1990-01-26",
        },
        {
            "driverId": "unmatched_driver",
            "givenName": "Nobody",
            "familyName": "Unknown",
            "dateOfBirth": "1900-01-01",
        },
    ]
    jolpica_constructors = [{"constructorId": "mercedes", "name": "Mercedes"}]
    jolpica_circuits = [{"circuitId": "monza", "circuitName": "Monza"}]

    overrides = {
        "driver": {"unmatched_driver": "lewis-hamilton"},
        "constructor": {},
        "circuit": {},
    }

    mapping, override_counts, excluded_counts, unresolved = build_id_map(
        conn, overrides, jolpica_drivers, jolpica_constructors, jolpica_circuits
    )

    assert mapping["driver"]["max_verstappen"] == "max-verstappen"
    assert mapping["driver"]["perez"] == "sergio-perez"
    assert mapping["driver"]["unmatched_driver"] == "lewis-hamilton"
    assert override_counts["driver"] == 1
    assert excluded_counts["driver"] == 0
    assert mapping["constructor"]["mercedes"] == "mercedes"
    assert mapping["circuit"]["monza"] == "monza"
    assert unresolved == {"driver": [], "constructor": [], "circuit": []}


def test_build_id_map_reports_unresolved_without_override(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)

    jolpica_drivers = [
        {
            "driverId": "unmatched_driver",
            "givenName": "Nobody",
            "familyName": "Unknown",
            "dateOfBirth": "1900-01-01",
        },
    ]
    overrides = {"driver": {}, "constructor": {}, "circuit": {}}

    mapping, override_counts, excluded_counts, unresolved = build_id_map(
        conn, overrides, jolpica_drivers, [], []
    )

    assert unresolved["driver"] == ["unmatched_driver"]
    assert mapping["driver"] == {}
    assert override_counts["driver"] == 0
    assert excluded_counts["driver"] == 0


def test_build_id_map_null_override_excludes_without_marking_unresolved(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)

    jolpica_drivers = [
        {
            "driverId": "ghost_entrant",
            "givenName": "Ghost",
            "familyName": "Entrant",
            "dateOfBirth": "1900-01-01",
        },
    ]
    # a JSON null in id_overrides.json means "confirmed: no f1db counterpart exists"
    overrides = {"driver": {"ghost_entrant": None}, "constructor": {}, "circuit": {}}

    mapping, override_counts, excluded_counts, unresolved = build_id_map(
        conn, overrides, jolpica_drivers, [], []
    )

    assert mapping["driver"] == {}
    assert unresolved["driver"] == []
    assert excluded_counts["driver"] == 1
    assert override_counts["driver"] == 0


def test_write_id_map_is_idempotent(tmp_path):
    conn = _make_f1db_conn(tmp_path)
    ensure_schema(conn)
    mapping = {"driver": {"max_verstappen": "max-verstappen"}, "constructor": {}, "circuit": {}}

    write_id_map(conn, mapping)
    write_id_map(conn, mapping)  # rebuild via DELETE+INSERT must not raise / duplicate

    rows = conn.execute("SELECT * FROM id_map").fetchall()
    assert len(rows) == 1
    assert rows[0]["f1db_id"] == "max-verstappen"


# --------------------------------------------------------------------------
# id_overrides.json loading
# --------------------------------------------------------------------------


def test_load_overrides_reads_json(tmp_path):
    path = tmp_path / "id_overrides.json"
    path.write_text(json.dumps({"driver": {"foo": "bar"}, "constructor": {}, "circuit": {}}))
    overrides = load_overrides(path)
    assert overrides["driver"] == {"foo": "bar"}
    assert overrides["constructor"] == {}
    assert overrides["circuit"] == {}


def test_load_overrides_missing_file_returns_empty(tmp_path):
    overrides = load_overrides(tmp_path / "does_not_exist.json")
    assert overrides == {"driver": {}, "constructor": {}, "circuit": {}}


def test_shipped_id_overrides_file_is_valid_json():
    from pitstop.db.seed import OVERRIDES_PATH

    assert OVERRIDES_PATH.exists()
    data = json.loads(OVERRIDES_PATH.read_text())
    assert set(data.keys()) >= {"driver", "constructor", "circuit"}

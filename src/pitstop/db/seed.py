"""One-time seed pipeline: fork the f1db sqlite database into pitstop's own copy.

Copies (or downloads) the f1db database, adds pitstop-owned tables (``meta``,
``id_map``, ``lap_time``), and builds an ``id_map`` that resolves Jolpica
(Ergast-style) entity ids to f1db entity ids for drivers, constructors and
circuits. Ongoing updates after this one-time seed come from
``pitstop-db-update`` (a separate, later tool) which reads Jolpica deltas and
writes them in using this id_map.

Usage:
    uv run pitstop-db-seed --out ./f1db.db
    uv run pitstop-db-seed --source /path/to/f1db.db --out ./f1db.db
    uv run pitstop-db-seed --source /path/to/f1db-sqlite.zip --out ./f1db.db
"""

import argparse
import io
import json
import re
import shutil
import sqlite3
import sys
import time
import unicodedata
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from pitstop.clients import jolpica_client
from pitstop.exceptions import DataSourceError

F1DB_LATEST_RELEASE_API = "https://api.github.com/repos/f1db/f1db/releases/latest"
F1DB_ASSET_NAME = "f1db-sqlite.zip"
OVERRIDES_PATH = Path(__file__).parent / "id_overrides.json"

PAGE_LIMIT = 100
SLEEP_S = 0.3
VALIDATION_SEASONS = range(2020, 2027)

ENTITIES = ("driver", "constructor", "circuit")


# --------------------------------------------------------------------------
# Name normalization + matching (pure functions, unit-testable offline)
# --------------------------------------------------------------------------


def normalize_name(s: str) -> str:
    """Lowercase, strip accents, collapse whitespace/hyphens for fuzzy matching."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[-_]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def match_driver(jolpica_driver: dict, candidates_by_dob: dict[str, list[dict]]) -> str | None:
    """Resolve one Jolpica driver dict to an f1db driver id, or None if ambiguous/unmatched.

    candidates_by_dob maps date_of_birth -> list of f1db driver rows (dicts with
    id/name/full_name/first_name/last_name).
    """
    dob = jolpica_driver.get("dateOfBirth")
    candidates = candidates_by_dob.get(dob, [])
    if not candidates:
        return None

    full = f"{jolpica_driver['givenName']} {jolpica_driver['familyName']}"
    norm_full = normalize_name(full)
    exact = [
        c
        for c in candidates
        if normalize_name(c["full_name"]) == norm_full or normalize_name(c["name"]) == norm_full
    ]
    if len(exact) == 1:
        return exact[0]["id"]
    if len(exact) > 1:
        return None

    norm_family = normalize_name(jolpica_driver["familyName"])
    family_matches = [c for c in candidates if normalize_name(c["last_name"]) == norm_family]
    if len(family_matches) == 1:
        return family_matches[0]["id"]
    return None


def match_by_name(name: str, rows: list[dict]) -> str | None:
    """Resolve a plain name (constructor/circuit) against f1db rows with name/full_name."""
    norm = normalize_name(name)
    exact = [
        r
        for r in rows
        if normalize_name(r["name"]) == norm or normalize_name(r["full_name"]) == norm
    ]
    if len(exact) == 1:
        return exact[0]["id"]
    return None


# --------------------------------------------------------------------------
# Source acquisition
# --------------------------------------------------------------------------


def _extract_db_member(zf: zipfile.ZipFile, out: Path) -> None:
    db_names = [n for n in zf.namelist() if n.endswith(".db")]
    if not db_names:
        raise SystemExit(f"no .db file found inside zip: {zf.namelist()}")
    with zf.open(db_names[0]) as src, open(out, "wb") as dst:
        shutil.copyfileobj(src, dst)


def download_latest_f1db() -> tuple[str, bytes]:
    """Download the latest f1db sqlite release. Returns (tag_name, zip_bytes)."""
    with urllib.request.urlopen(F1DB_LATEST_RELEASE_API) as r:
        release = json.load(r)
    tag = release["tag_name"]
    asset = next(a for a in release["assets"] if a["name"] == F1DB_ASSET_NAME)
    with urllib.request.urlopen(asset["browser_download_url"]) as r:
        zip_bytes = r.read()
    return tag, zip_bytes


def copy_source(source: str | None, out: Path) -> str:
    """Populate `out` with the f1db sqlite database. Returns the seeded_from tag."""
    if source is None:
        tag, zip_bytes = download_latest_f1db()
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            _extract_db_member(zf, out)
        return tag

    p = Path(source)
    if p.suffix == ".zip":
        with zipfile.ZipFile(p) as zf:
            _extract_db_member(zf, out)
    elif p.resolve() != out.resolve():
        shutil.copy(p, out)
    return "local"


# --------------------------------------------------------------------------
# Jolpica pagination
# --------------------------------------------------------------------------


# ponytail: exponential 5..80s on 429 only; upgrade to Retry-After parsing if
# this ever proves insufficient.
@retry(
    retry=retry_if_exception(lambda e: isinstance(e, DataSourceError) and "429" in e.reason),
    wait=wait_exponential(multiplier=5, min=5, max=80),
    stop=stop_after_attempt(6),
    reraise=True,
)
def _query(path: str, **params) -> dict:
    """jolpica_client.query with backoff on 429s — the shared public Jolpica
    proxy rate-limits by more than just our own request rate."""
    return jolpica_client.query(path, **params)


def _paginate(path: str, table_key: str, item_key: str) -> list[dict]:
    items: list[dict] = []
    offset = 0
    while True:
        data = _query(path, limit=PAGE_LIMIT, offset=offset)
        mr = data["MRData"]
        total = int(mr["total"])
        items.extend(mr[table_key][item_key])
        offset += PAGE_LIMIT
        if offset >= total:
            break
        time.sleep(SLEEP_S)
    return items


def fetch_all_drivers() -> list[dict]:
    return _paginate("drivers", "DriverTable", "Drivers")


def fetch_all_constructors() -> list[dict]:
    return _paginate("constructors", "ConstructorTable", "Constructors")


def fetch_all_circuits() -> list[dict]:
    return _paginate("circuits", "CircuitTable", "Circuits")


# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS id_map (
            entity TEXT NOT NULL,
            ergast_id TEXT NOT NULL,
            f1db_id TEXT NOT NULL,
            PRIMARY KEY (entity, ergast_id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lap_time (
            race_id INTEGER NOT NULL,
            driver_id TEXT NOT NULL,
            lap INTEGER NOT NULL,
            position INTEGER,
            time TEXT,
            time_millis INTEGER,
            PRIMARY KEY (race_id, driver_id, lap)
        )
        """
    )
    conn.commit()


def write_meta(conn: sqlite3.Connection, seeded_from: str) -> None:
    today = datetime.now(UTC).date().isoformat()
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', '1')")
    conn.execute(
        "INSERT OR IGNORE INTO meta (key, value) VALUES ('seeded_from', ?)", (seeded_from,)
    )
    conn.execute("INSERT OR IGNORE INTO meta (key, value) VALUES ('seeded_at', ?)", (today,))
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_updated', ?)", (today,))
    conn.commit()


# --------------------------------------------------------------------------
# id_map build
# --------------------------------------------------------------------------


def load_overrides(path: Path = OVERRIDES_PATH) -> dict[str, dict[str, str | None]]:
    if not path.exists():
        return {e: {} for e in ENTITIES}
    with open(path) as f:
        data = json.load(f)
    return {e: data.get(e, {}) for e in ENTITIES}


def _driver_rows(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    rows = conn.execute(
        "SELECT id, name, full_name, first_name, last_name, date_of_birth FROM driver"
    ).fetchall()
    by_dob: dict[str, list[dict]] = {}
    for r in rows:
        by_dob.setdefault(r["date_of_birth"], []).append(dict(r))
    return by_dob


def _rows(conn: sqlite3.Connection, table: str) -> list[dict]:
    rows = conn.execute(f"SELECT id, name, full_name FROM {table}").fetchall()
    return [dict(r) for r in rows]


_EXCLUDED = object()  # sentinel: override explicitly says "no f1db counterpart exists"


def _resolve(ergast_id: str, matched: str | None, overrides_entity: dict[str, str | None]):
    """Combine an auto-match with the overrides file.

    Returns the f1db id, None (still unresolved), or _EXCLUDED if the overrides
    file explicitly records (via a JSON null) that this entity has no f1db
    counterpart — e.g. a historical entrant who withdrew before ever taking
    part, so f1db never created a row for them.
    """
    if matched is not None:
        return matched
    if ergast_id in overrides_entity:
        override = overrides_entity[ergast_id]
        return _EXCLUDED if override is None else override
    return None


def build_id_map(
    conn: sqlite3.Connection,
    overrides: dict[str, dict[str, str]],
    jolpica_drivers: list[dict] | None = None,
    jolpica_constructors: list[dict] | None = None,
    jolpica_circuits: list[dict] | None = None,
) -> tuple[dict[str, dict[str, str]], dict[str, int], dict[str, int], dict[str, list[str]]]:
    """Build the id_map. Returns (mapping, override_counts, excluded_counts, unresolved).

    mapping: entity -> {ergast_id: f1db_id} for everything resolved.
    override_counts: entity -> number of entries resolved only via overrides.
    excluded_counts: entity -> number of entries the overrides file marked as
        having no f1db counterpart (JSON null) — deliberately left unmapped.
    unresolved: entity -> [ergast_id, ...] still unresolved after overrides.
    """
    conn.row_factory = sqlite3.Row

    jolpica_drivers = jolpica_drivers if jolpica_drivers is not None else fetch_all_drivers()
    jolpica_constructors = (
        jolpica_constructors if jolpica_constructors is not None else fetch_all_constructors()
    )
    jolpica_circuits = jolpica_circuits if jolpica_circuits is not None else fetch_all_circuits()

    dob_map = _driver_rows(conn)
    constructor_rows = _rows(conn, "constructor")
    circuit_rows = _rows(conn, "circuit")

    mapping: dict[str, dict[str, str]] = {e: {} for e in ENTITIES}
    override_counts: dict[str, int] = {e: 0 for e in ENTITIES}
    excluded_counts: dict[str, int] = {e: 0 for e in ENTITIES}
    unresolved: dict[str, list[str]] = {e: [] for e in ENTITIES}

    def record(entity: str, ergast_id: str, matched: str | None) -> None:
        f1db_id = _resolve(ergast_id, matched, overrides[entity])
        if f1db_id is _EXCLUDED:
            excluded_counts[entity] += 1
        elif f1db_id is None:
            unresolved[entity].append(ergast_id)
        else:
            if matched is None:
                override_counts[entity] += 1
            mapping[entity][ergast_id] = f1db_id

    for jd in jolpica_drivers:
        record("driver", jd["driverId"], match_driver(jd, dob_map))

    for jc in jolpica_constructors:
        record("constructor", jc["constructorId"], match_by_name(jc["name"], constructor_rows))

    for jc in jolpica_circuits:
        record("circuit", jc["circuitId"], match_by_name(jc["circuitName"], circuit_rows))

    return mapping, override_counts, excluded_counts, unresolved


def write_id_map(conn: sqlite3.Connection, mapping: dict[str, dict[str, str]]) -> None:
    conn.execute("DELETE FROM id_map")
    for entity, entries in mapping.items():
        conn.executemany(
            "INSERT INTO id_map (entity, ergast_id, f1db_id) VALUES (?, ?, ?)",
            [(entity, ergast_id, f1db_id) for ergast_id, f1db_id in entries.items()],
        )
    conn.commit()


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------


def validate(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """Assert every 2020-2026 season entity is in id_map. Returns missing ids by entity."""
    mapped: dict[str, set[str]] = {}
    for entity in ENTITIES:
        rows = conn.execute("SELECT ergast_id FROM id_map WHERE entity = ?", (entity,)).fetchall()
        mapped[entity] = {r["ergast_id"] for r in rows}

    missing: dict[str, list[str]] = {e: [] for e in ENTITIES}
    for year in VALIDATION_SEASONS:
        drivers = _query(f"{year}/drivers")["MRData"]["DriverTable"]["Drivers"]
        time.sleep(SLEEP_S)
        constructors = _query(f"{year}/constructors")["MRData"]["ConstructorTable"]["Constructors"]
        time.sleep(SLEEP_S)
        circuits = _query(f"{year}/circuits")["MRData"]["CircuitTable"]["Circuits"]
        time.sleep(SLEEP_S)

        for d in drivers:
            if d["driverId"] not in mapped["driver"]:
                missing["driver"].append(d["driverId"])
        for c in constructors:
            if c["constructorId"] not in mapped["constructor"]:
                missing["constructor"].append(c["constructorId"])
        for c in circuits:
            if c["circuitId"] not in mapped["circuit"]:
                missing["circuit"].append(c["circuitId"])

    count_2026 = conn.execute(
        "SELECT COUNT(*) FROM race_data WHERE race_id IN (SELECT id FROM race WHERE year = 2026)"
    ).fetchone()[0]
    if count_2026 <= 1000:
        missing.setdefault("_race_data_2026", []).append(str(count_2026))

    return missing


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed pitstop's f1db-derived database.")
    parser.add_argument(
        "--source",
        default=None,
        help="Path to an f1db.db or f1db-sqlite.zip. Default: download the latest f1db release.",
    )
    parser.add_argument("--out", default="./f1db.db", help="Output database path.")
    args = parser.parse_args()

    out = Path(args.out)
    print(f"[seed] copying source into {out} ...")
    seeded_from = copy_source(args.source, out)
    print(f"[seed] seeded_from={seeded_from}")

    conn = sqlite3.connect(out)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)

    overrides = load_overrides()
    print("[seed] fetching Jolpica drivers/constructors/circuits (paginated)...")
    mapping, override_counts, excluded_counts, unresolved = build_id_map(conn, overrides)

    if any(unresolved.values()):
        print("\n[seed] UNRESOLVED entities after overrides:")
        for entity, ids in unresolved.items():
            if ids:
                print(f"  {entity} ({len(ids)}): {ids}")
        print(f"\nAdd mappings to {OVERRIDES_PATH} and re-run.")
        sys.exit(1)

    write_id_map(conn, mapping)
    write_meta(conn, seeded_from)

    print("[seed] validating 2020-2026 season coverage...")
    missing = validate(conn)
    if any(missing.values()):
        print("\n[seed] VALIDATION FAILED — missing from id_map or race_data:")
        for key, ids in missing.items():
            if ids:
                print(f"  {key}: {ids}")
        sys.exit(1)

    print("\n[seed] coverage summary:")
    for entity in ENTITIES:
        n = len(mapping[entity])
        print(
            f"  {entity}: {n} mapped ({override_counts[entity]} via overrides, "
            f"{excluded_counts[entity]} confirmed absent from f1db)"
        )
    print(f"  db: {out}")
    conn.close()


if __name__ == "__main__":
    main()

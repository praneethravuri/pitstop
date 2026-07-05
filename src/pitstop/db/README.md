# pitstop.db — one-time f1db seed

`seed.py` forks the [f1db](https://github.com/f1db/f1db) sqlite database into
pitstop's own `f1db.db`: it copies the source db, adds our tables
(`meta`, `id_map`, `lap_time`), and builds `id_map` by matching every
Jolpica driver/constructor/circuit id to its f1db counterpart.

Run once, at v0.5.0 release time:

```
uv run pitstop-db-seed --out ./f1db.db
```

Unresolved matches are hand-curated in `id_overrides.json` — re-run until
the validation summary is clean.

Ongoing updates (new races, results, standings) come from a separate tool,
`pitstop-db-update` (Step 2), which reads Jolpica deltas using this id_map.
This is a one-time fork, not a live mirror.

f1db data is licensed [CC-BY-4.0](https://github.com/f1db/f1db#license);
attribution: f1db (https://github.com/f1db/f1db).

## pitstop-db-update

Keeps the forked database current from Jolpica, removing any dependency on
f1db.com releases going forward. Finds races that have happened but have no
`RACE_RESULT` rows yet, and writes results, qualifying, sprint, pit stops,
lap times and standings using the `id_map` built by the seed step.

```
uv run pitstop-db-update --db ./f1db.db              # update from the current year onward
uv run pitstop-db-update --db ./f1db.db --dry-run    # preview planned races + row counts
uv run pitstop-db-update --db ./f1db.db --year 2024  # update from an earlier year onward
uv run pitstop-db-update --db ./f1db.db --backfill-laps 2023  # fill in missing lap_time only
```

Idempotent (DELETE+INSERT per race), safe to re-run. Intended to run weekly
via GitHub Actions after each race weekend.

# CockroachDB Data Locality PoC

This repo is a proof of concept for CockroachDB multi-region data locality on a specific topology: **three regions, two of which run applications**.

- **East (`us-east`)** — runs applications
- **West (`us-west`)** — runs applications
- **Central (`us-central`)** — the quorum tiebreaker that lets the cluster survive a full region failure; no application data is homed there (it could take on other roles later)

It demonstrates the two table locality strategies and the trade-offs between them:

- **GLOBAL** (`trailer_global`) — optimized for fast, present-time reads from every region, paid for with slow writes. Choose this for a table if:
  1. it needs to be optimized for fast reading in all regions
  2. `INSERT`s, `UPDATE`s and `DELETE`s happen infrequently or even ocassionally
  3. slightly increased write latency can be tolerated
- **REGIONAL BY ROW** (`trailer_rbr`) — optimized for fast local reads and writes in the region that owns each row. Choose this for a table if:
  1. it needs to be optimized for fast `INSERT`s, `UPDATE`s and `DELETE`s in multiple regions
  2. `SELECT`s are typically predicated on specific values, e.g. `id='12345'`

Rows are homed by trailer-number prefix: `TRL-EAST-*` → `us-east`, `TRL-WEST-*` → `us-west`. Anything else lands in `us-central` — a catch-all that doubles as an accident audit (`SELECT count(*) FROM trailer_rbr WHERE region = 'us-central'` should be zero).

## What's in the repo

| File | Purpose |
|------|---------|
| `schema.sql` | Canonical DDL for `trailer_global` and `trailer_rbr` — the only copy; this README deliberately repeats none of it |
| `Trailers.py` | dbworkload class exercising both tables; measures the latency profile of each locality strategy per region |
| `datagen.py` | Shared synthetic-data generation (trailer info vocabulary, prefixes); imported by `Trailers.py` and `region-hopper.py` |
| `region-hopper.py` | Cross-region visibility probe: writes through one gateway, verifies identical visibility through all others |
| `show-ranges.py` | Reports how a table's rows are distributed across ranges (leaseholder and replica placement) |
| `Dockerfile` | Packages `Trailers.py` as a dbworkload runner image |
| `config.yaml.tmpl` | Template for `region-hopper.py`'s per-region connection URLs (`config.yaml` itself is gitignored) |
| `requirements.txt` | Host-side Python dependencies |

## Cluster setup

Add the regions and set the survival objective:

```sql
ALTER DATABASE regionalpoc SET PRIMARY REGION "us-east";
ALTER DATABASE regionalpoc ADD REGION "us-west";
ALTER DATABASE regionalpoc ADD REGION "us-central";
ALTER DATABASE regionalpoc SURVIVE REGION FAILURE;
```

Then apply the DDL from `schema.sql`.

### Checking range placement

`show-ranges.py` shows which ranges hold a table's rows, and where their leaseholders and replicas live:

```bash
python3 show-ranges.py --url <url> --table trailer_global
```

Illustrative output — a GLOBAL table's rows in one range, with every region holding at least one replica:

```
┌───┬──────────┬──────┬─────────────┬────────────────────────────────────────────────────────────────────┐
│   │ range_id │ rows │ leaseholder │ replicas                                                           │
╞───╪══════════╪══════╪═════════════╪════════════════════════════════════════════════════════════════════╡
│ 1 │ 3806     │ 100  │ us-east (3) │ us-east (1), us-east (3), us-east (6), us-west (5), us-central (8) │
├───┼──────────┼──────┼─────────────┼────────────────────────────────────────────────────────────────────┤
│   │ TOTAL    │ 100  │             │                                                                    │
└───┴──────────┴──────┴─────────────┴────────────────────────────────────────────────────────────────────┘
```

The zone configuration confirms the same:

```sql
> SHOW ZONE CONFIGURATION FROM TABLE trailer_global;
         target        |                            raw_config_sql
-----------------------+------------------------------------------------------------------------
  TABLE trailer_global | ALTER TABLE trailer_global CONFIGURE ZONE USING
                       |     range_min_bytes = 134217728,
                       |     range_max_bytes = 536870912,
                       |     gc.ttlseconds = 31536000,
                       |     global_reads = true,
                       |     num_replicas = 5,
                       |     num_voters = 3,
                       |     constraints = '{+region=us-east: 1, +region=us-west: 1, +region=us-central: 1}',
                       |     voter_constraints = '[+region=us-east]',
                       |     lease_preferences = '[[+region=us-east]]'
```

## The workload: dbworkload + Trailers.py

`Trailers.py` is a [dbworkload](https://github.com/cockroachdb/dbworkload) class. Each worker thread runs six functions per pass, and dbworkload reports latency percentiles per function — one stats line per claim being proven:

| Function | What it proves |
|----------|----------------|
| `global_insert`, `global_update` | GLOBAL write cost — slow from every region (the price of global reads) |
| `global_select` | GLOBAL read speed — fast, present-time, from every region |
| `rbr_insert`, `rbr_update` | RBR local write speed — single-region-class latency |
| `rbr_select` | RBR local read speed — the fastest operation on the board |

The gateway region is implicit in the connection URL: the class discovers it (`gateway_region()`) at startup and pins its RBR operations to it. Target rows are sampled once at startup from existing data; trailer numbers for inserts are generated server-side (`prefix || unique_rowid()`), so they never collide with the unique indexes.

### Args

Passed as a JSON object via `--args`:

- `prefix` (required) — `"TRL-EAST-"` or `"TRL-WEST-"`; must correspond to the gateway URL's region.
- `rows` (optional) — maintain each table at this many rows, half per prefix: `setup()` counts each prefix's rows and fills any deficit or trims any excess before the run starts. Only honored at `-c 1` (silently ignored at higher concurrency) — run it as a dedicated maintenance invocation. Required before first use on an empty database. Between maintenance runs, counts drift upward by one row per table per completed loop pass — the workload keeps inserting as part of its measured functions.

### Running directly

Maintenance run — fill or trim both tables to the target counts (single-threaded by design):

```bash
dbworkload run -w Trailers.py \
  --uri "postgresql://<user>:<pass>@<east-gateway>:26257/regionalpoc?sslmode=verify-full" \
  --args '{"prefix": "TRL-EAST-", "rows": 1000000}' \
  -c 1 -i 1
```

Measured run:

```bash
dbworkload run -w Trailers.py \
  --uri "postgresql://<user>:<pass>@<east-gateway>:26257/regionalpoc?sslmode=verify-full" \
  --args '{"prefix": "TRL-EAST-"}' \
  -c 10 -d 60
```

Run one process per application region (East URL with `TRL-EAST-`, West URL with `TRL-WEST-`) over the same window and compare the per-function stats side by side.

### Running in Docker

```bash
docker build -t trailers .
docker run --rm trailers --uri "..." --args '{"prefix": "TRL-EAST-"}' -c 10 -d 60
```

The image hardcodes only `dbworkload run -w Trailers.py`; every argument after the image name passes through to dbworkload untouched. Certificates are part of the URI — if it references a cert file path, mount it (`-v /path/to/certs:/path/to/certs:ro`).

## The probe: region-hopper.py

Demonstrates that the cluster is one consistent database regardless of entry point: each iteration inserts a row into both tables through a randomly chosen regional gateway, then reads them back through every other gateway and verifies the values and the `crdb_internal_mvcc_timestamp` are identical — read-your-writes across regions, with per-gateway timings printed. Any mismatch stops the probe.

```bash
cp config.yaml.tmpl config.yaml   # fill in the per-region connection URLs
python3 region-hopper.py
```

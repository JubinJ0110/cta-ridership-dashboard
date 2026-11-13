# dbt project — CTA ridership (analytics engineering)

A dbt project on the same CTA daily-boarding data as the dashboard in this
repo. It turns the raw `ridership` table into clean, tested, documented
models — the standard analytics-engineering workflow (SQL models + tests +
docs) that data teams run on warehouse data, here with DuckDB locally so
there is no cloud account and no cost.

## Data

Source: `data/ridership.sqlite`, table `ridership` — one row per day,
2001–present (9,374 rows; currently through 2026-08-31). Columns:
`service_date` (TEXT, primary key), `day_type` (`W` weekday, `A` Saturday,
`U` Sunday/holiday), `bus`, `rail_boardings`, `total_rides`.

The SQLite file is attached read-only by the dbt profile, so dbt always
reads the live table maintained by `fetch_ridership.py` and never modifies
it. The dashboard cron keeps refreshing that file; re-running `dbt build`
picks up new days.

## Models

Lineage: `cta.ridership` → `stg_ridership` → `int_daily_totals` → marts.

- **staging / `stg_ridership`** — cleans the raw table: casts
  `service_date` to a date, keeps the five raw columns as-is.
- **intermediate / `int_daily_totals`** — one row per day with `bus_share`
  and `rail_share` plus `year`/`month` keys for the marts.
- **marts / `monthly_summary`** — monthly totals, average daily rides,
  and days in month.
- **marts / `bus_vs_rail_recovery`** — each month's bus, rail, and total
  rides as a percentage of the same calendar month in 2019. Over the last
  12 months bus is back to ~85% of 2019 while rail is only ~65% — rail is
  not closing the gap.
- **marts / `yoy_monthly`** — each month vs the same month a year earlier,
  with the year-over-year change and percentage change.

## Tests

Run with `dbt build` (models + tests together) or `dbt test` alone:

- `service_date` is unique and not null (schema tests on `stg_ridership`).
- `day_type` is one of `W`, `A`, `U`.
- `total_rides = bus + rail_boardings` on every row.
- `bus` and `rail_boardings` are never negative.
- No `service_date` in the future.

A bad data fetch fails loudly here instead of quietly charting bad numbers.

## Run it

```bash
cd dbt
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/dbt build --profiles-dir .
.venv/bin/dbt docs generate --profiles-dir .   # then `dbt docs serve`
```

Two environment notes (both already handled on this machine, recorded
here so a fresh setup doesn't stall):

- **Proxy:** DuckDB 2.x cannot parse this machine's credentialed
  `http_proxy`/`https_proxy` variables, so run dbt with them unset:
  `env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY dbt ...`
  DuckDB only touches local files here, so no proxy is needed.
- **SQLite extension:** DuckDB 2.x renamed it `sqlite_scanner` and tries to
  download it on first use. It is already installed in
  `~/.duckdb/extensions/` on this machine. On a fresh machine, fetch it
  once before the first run:
  `curl -sL -o /tmp/sqlite_scanner.duckdb_extension.gz https://extensions.duckdb.org/v2.0.0/linux_amd64/sqlite_scanner.duckdb_extension.gz`
  then `duckdb -c "INSTALL '/tmp/sqlite_scanner.duckdb_extension.gz'"`.

Outputs land in the local `dev.duckdb` file (gitignored). The dashboard
itself is untouched — this folder only reads its data.

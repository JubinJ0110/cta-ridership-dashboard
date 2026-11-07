#!/usr/bin/env python3
"""Fetch CTA daily ridership totals from the Chicago Data Portal and load them
into a local SQLite database.

Source: Chicago Data Portal (Socrata API), dataset
"CTA - Ridership - Daily Boarding Totals"
https://data.cityofchicago.org/resource/6iiy-9s97.json

Columns: service_date, day_type (W=Weekday, A=Saturday, U=Sunday/Holiday),
bus, rail_boardings, total_rides.

No API key needed. The script is incremental: on the first run it loads the
full history (back to 2001); on later runs it only fetches dates newer than
what is already in the database.

Usage:
    python3 fetch_ridership.py
"""

import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

import urllib.request
import urllib.parse

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ridership.sqlite"
API_URL = "https://data.cityofchicago.org/resource/6iiy-9s97.json"

PAGE_SIZE = 50000


def fetch_page(params):
    """Fetch one page of rows from the Socrata API. Returns a list of dicts."""
    query = urllib.parse.urlencode(params)
    url = f"{API_URL}?{query}"
    headers = {"Accept": "application/json"}
    if requests is not None:
        resp = requests.get(url, headers=headers, timeout=60)
        resp.raise_for_status()
        return resp.json()
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def ensure_db(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ridership (
            service_date TEXT PRIMARY KEY,
            day_type TEXT,
            bus INTEGER,
            rail_boardings INTEGER,
            total_rides INTEGER
        )
        """
    )
    conn.commit()


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    ensure_db(conn)

    row = conn.execute("SELECT MAX(service_date) FROM ridership").fetchone()
    max_date = row[0] if row and row[0] else None

    if max_date:
        where = f"service_date > '{max_date}'"
        print(f"Existing data through {max_date}; fetching newer rows only.")
    else:
        where = None
        print("No existing data; fetching full history (2001 to present).")

    total_inserted = 0
    offset = 0
    while True:
        params = {
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "service_date ASC",
        }
        if where:
            params["$where"] = where
        try:
            rows = fetch_page(params)
        except Exception as exc:  # noqa: BLE001 - report and stop cleanly
            print(f"Error fetching from API: {exc}", file=sys.stderr)
            conn.close()
            sys.exit(1)

        if not rows:
            break

        with conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO ridership
                    (service_date, day_type, bus, rail_boardings, total_rides)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        r["service_date"][:10],
                        r.get("day_type"),
                        int(r["bus"]) if r.get("bus") is not None else None,
                        int(r["rail_boardings"])
                        if r.get("rail_boardings") is not None
                        else None,
                        int(r["total_rides"])
                        if r.get("total_rides") is not None
                        else None,
                    )
                    for r in rows
                ],
            )
        total_inserted += len(rows)
        print(f"Fetched {len(rows)} rows (offset {offset}).")
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    count, first, last = conn.execute(
        "SELECT COUNT(*), MIN(service_date), MAX(service_date) FROM ridership"
    ).fetchone()
    conn.close()

    print(f"Rows fetched this run: {total_inserted}")
    print(f"Database now holds {count} days, {first} to {last}.")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    main()

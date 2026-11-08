#!/usr/bin/env python3
"""Build data/monthly_summary.csv from data/ridership.sqlite.

One row per month: total rides, bus, rail, and service days.
Run: python3 monthly_summary.py
"""
import csv
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "data", "monthly_summary.csv")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT strftime('%Y-%m', service_date) AS month,
               SUM(total_rides) AS total_rides,
               SUM(bus) AS bus,
               SUM(rail_boardings) AS rail,
               COUNT(*) AS days
        FROM ridership
        GROUP BY month
        ORDER BY month
        """
    ).fetchall()
    con.close()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", "total_rides", "bus", "rail_boardings", "days"])
        w.writerows(rows)
    print(f"wrote {len(rows)} months to {OUT}")


if __name__ == "__main__":
    main()

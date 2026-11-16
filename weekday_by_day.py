#!/usr/bin/env python3
"""Weekday-by-weekday recovery: Mon-Fri average rides, latest 12 months vs 2019.

The shipped weekday chart only splits W/A/U. Deriving the weekday from
service_date shows whether the weekday lag is uniform or concentrated
on Mon/Fri (hybrid-work pattern).

Run: python3 weekday_by_day.py  (reads data/ridership.sqlite, writes
charts/weekday_by_day.png)
"""
import datetime
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "weekday_by_day.png")
NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def avg(rows):
    return sum(r[4] for r in rows) / len(rows) if rows else 0


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, day_type, bus, rail_boardings, total_rides "
        "FROM ridership"
    ).fetchall()
    con.close()
    base, recent = {}, {}
    for wd in range(5):
        b = [r for r in rows if r[0].startswith("2019")
             and datetime.date.fromisoformat(r[0]).weekday() == wd
             and r[1] == "W"]
        r = [r for r in rows
             if ((r[0] >= "2025-09-01" and r[0] <= "2026-08-31"))
             and datetime.date.fromisoformat(r[0]).weekday() == wd
             and r[1] == "W"]
        base[wd], recent[wd] = avg(b), avg(r)
        print(f"{NAMES[wd]}: 2019 {avg(b):,.0f} -> latest 12m {avg(r):,.0f} "
              f"= {100 * avg(r) / avg(b):.1f}% of 2019")
    pct = [100 * recent[wd] / base[wd] for wd in range(5)]
    fig, ax = plt.subplots()
    ax.bar(NAMES, pct)
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of 2019 average")
    ax.set_title("Weekday recovery by day of week (latest 12 months vs 2019)")
    for i, v in enumerate(pct):
        ax.text(i, v + 1, f"{v:.1f}%", ha="center")
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

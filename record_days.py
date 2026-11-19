#!/usr/bin/env python3
"""Record days and the 2026 projection: how far is the best day from normal?

Finds the highest/lowest single days all-time and post-COVID, and
projects the full 2026 total from the Jan-Aug pace vs 2025.

Run: python3 record_days.py  (reads data/ridership.sqlite, no chart;
prints findings)
"""
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, day_type, bus, rail_boardings, total_rides "
        "FROM ridership"
    ).fetchall()
    con.close()
    top = sorted(rows, key=lambda r: r[4], reverse=True)[:5]
    print("Top 5 days all-time:")
    for r in top:
        print(f"  {r[0]} ({r[1]}): {r[4]:,} rides")
    post = [r for r in rows if r[0] >= "2021-01-01"]
    best = max(post, key=lambda r: r[4])
    print(f"Best post-COVID day: {best[0]}: {best[4]:,} rides "
          f"(bus {best[2]:,}, rail {best[3]:,})")
    print(f"  vs 2019 weekday average 1,468,731: "
          f"{100 * best[4] / 1468731:.1f}%")
    ja26 = sum(t for d, _, _, _, t in rows
               if d.startswith("2026") and int(d[5:7]) <= 8)
    ja25 = sum(t for d, _, _, _, t in rows
               if d.startswith("2025") and int(d[5:7]) <= 8)
    fy25 = sum(t for d, _, _, _, t in rows if d.startswith("2025"))
    proj = ja26 / ja25 * fy25
    print(f"2026 projection: {proj / 1e6:.1f}M rides "
          f"({100 * proj / 455.7e6:.1f}% of 2019)")


if __name__ == "__main__":
    main()

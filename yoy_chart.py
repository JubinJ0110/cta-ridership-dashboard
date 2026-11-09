#!/usr/bin/env python3
"""Year-over-year monthly ridership chart: one line per year, 2019-2026.

Run: python3 yoy_chart.py  (reads data/ridership.sqlite, writes
charts/yoy_monthly.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "yoy_monthly.png")
YEARS = [2019, 2020, 2023, 2024, 2025, 2026]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               CAST(strftime('%m', service_date) AS INTEGER) AS m,
               SUM(total_rides) AS rides
        FROM ridership
        GROUP BY y, m
        ORDER BY y, m
        """
    ).fetchall()
    con.close()
    by_year = {y: {} for y in YEARS}
    for y, m, rides in rows:
        if y in by_year:
            by_year[y][m] = rides / 1e6

    fig, ax = plt.subplots(figsize=(10, 5))
    for y in YEARS:
        months = sorted(by_year[y])
        ax.plot(months, [by_year[y][m] for m in months], marker="o",
                markersize=3, label=str(y))
    ax.set_title("CTA monthly rides by year (millions)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Million rides")
    ax.set_xticks(range(1, 13))
    ax.legend(ncol=3)
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

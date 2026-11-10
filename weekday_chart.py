#!/usr/bin/env python3
"""Average daily rides by day type, 2019 vs 2024 vs 2025.

Run: python3 weekday_chart.py  (reads data/ridership.sqlite, writes
charts/weekday_weekend.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "weekday_weekend.png")
YEARS = [2019, 2024, 2025]
LABELS = {"W": "Weekday", "A": "Saturday", "U": "Sunday / holiday"}


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               day_type,
               AVG(total_rides) AS avg_rides
        FROM ridership
        GROUP BY y, day_type
        ORDER BY y, day_type
        """
    ).fetchall()
    con.close()
    data = {y: {} for y in YEARS}
    for y, dt, avg in rows:
        if y in data:
            data[y][dt] = avg / 1000

    order = ["W", "A", "U"]
    x = range(len(order))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    for i, y in enumerate(YEARS):
        vals = [data[y].get(dt, 0) for dt in order]
        ax.bar([p + (i - 1) * width for p in x], vals, width, label=str(y))
    ax.set_title("Average daily rides by day type (thousands)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([LABELS[dt] for dt in order])
    ax.set_ylabel("Thousand rides per day")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

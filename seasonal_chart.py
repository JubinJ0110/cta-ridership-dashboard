#!/usr/bin/env python3
"""Seasonal month-of-year chart: average daily rides by calendar month.

Compares 2019 (pre-COVID baseline) with 2024 and 2025, so seasonality
is separated from the recovery trend. Uses average daily rides per
month, not monthly totals, so months of different lengths compare fairly.

Run: python3 seasonal_chart.py  (reads data/ridership.sqlite, writes
charts/seasonal_monthly.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "seasonal_monthly.png")
YEARS = [2019, 2024, 2025]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               CAST(strftime('%m', service_date) AS INTEGER) AS m,
               AVG(total_rides) AS avg_daily
        FROM ridership
        GROUP BY y, m
        ORDER BY y, m
        """
    ).fetchall()
    con.close()
    by_year = {y: {} for y in YEARS}
    for y, m, avg_daily in rows:
        if y in by_year:
            by_year[y][m] = avg_daily / 1e3

    fig, ax = plt.subplots(figsize=(10, 5))
    for y in YEARS:
        months = sorted(by_year[y])
        ax.plot(months, [by_year[y][m] for m in months], marker="o",
                markersize=3, label=str(y))
    ax.set_title("Average daily CTA rides by calendar month (thousands)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Thousand rides per day")
    ax.set_xticks(range(1, 13))
    ax.legend()
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")
    for y in YEARS:
        vals = [by_year[y][m] for m in sorted(by_year[y])]
        print(f"{y}: peak month {max(vals):.0f}k/day, trough {min(vals):.0f}k/day")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Day-type recovery by year: did weekends come back first?

Average daily rides for weekdays, Saturdays, and Sundays/holidays in
2021-2026, as % of the same day type's 2019 average. Extends the
mode-by-daytype snapshot (#11, latest 12 months) into a six-year trend.
2026 covers Jan-Sep only and is marked as such on the chart.

Run: python3 daytype_recovery.py  (reads data/ridership.sqlite, writes
charts/daytype_recovery_by_year.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "daytype_recovery_by_year.png")
YEARS = [2021, 2022, 2023, 2024, 2025, 2026]
TYPES = [("W", "Weekday"), ("A", "Saturday"), ("U", "Sun/Holiday")]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, day_type, total_rides FROM ridership"
    ).fetchall()
    con.close()

    def avg(y, dt):
        sel = [t for d, dty, t in rows
               if d.startswith(str(y)) and dty == dt]
        return sum(sel) / len(sel)

    base = {dt: avg(2019, dt) for dt, _ in TYPES}
    rec = {dt: [100 * avg(y, dt) / base[dt] for y in YEARS]
           for dt, _ in TYPES}
    for dt, name in TYPES:
        print(name, " ".join(f"{y} {rec[dt][i]:.1f}%"
                             for i, y in enumerate(YEARS)))
    print(f"2026 (Jan-Sep): weekday {rec['W'][-1]:.1f}%, "
          f"Saturday {rec['A'][-1]:.1f}%, "
          f"Sun/Holiday {rec['U'][-1]:.1f}% of 2019")

    fig, ax = plt.subplots()
    for dt, name in TYPES:
        ax.plot(YEARS, rec[dt], "o-", label=name)
    ax.set_xticks(YEARS)
    ax.set_xticklabels([str(y) for y in YEARS[:-1]] + ["2026*"])
    ax.set_ylabel("% of same day type in 2019")
    ax.set_title("Weekends recovered first — Sundays nearly fully back")
    ax.set_ylim(0, 100)
    ax.legend()
    ax.text(0.01, 0.03, "*2026 is Jan-Sep only", transform=ax.transAxes,
            fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

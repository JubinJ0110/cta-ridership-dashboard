#!/usr/bin/env python3
"""Weekday recovery trend: is Monday catching up?

Average daily rides for each weekday (Mon-Fri) in 2021-2025, as % of the
same weekday's 2019 average. Extends the weekday-by-weekday snapshot
(#10, one year) into a five-year trend.

Run: python3 weekday_trend.py  (reads data/ridership.sqlite, writes
charts/weekday_recovery_trend.png)
"""
import datetime
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "weekday_recovery_trend.png")
YEARS = [2021, 2022, 2023, 2024, 2025]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, total_rides FROM ridership").fetchall()
    con.close()
    by = {}
    for d, t in rows:
        y = int(d[:4])
        by.setdefault(y, {}).setdefault(
            datetime.date.fromisoformat(d).weekday(), []).append(t)
    avg = {y: {w: sum(v) / len(v) for w, v in by[y].items()}
           for y in by}
    rec = {y: [100 * avg[y][w] / avg[2019][w] for w in range(5)]
           for y in YEARS}
    for y in YEARS:
        print(y, " ".join(f"{DAYS[w]} {rec[y][w]:.1f}%"
                           for w in range(5)))
    print(f"Mon-Thu gap: 2023 {rec[2023][3] - rec[2023][0]:.1f} pts, "
          f"2025 {rec[2025][3] - rec[2025][0]:.1f} pts")

    fig, ax = plt.subplots()
    for w in range(5):
        ax.plot(YEARS, [rec[y][w] for y in YEARS], "o-", label=DAYS[w])
    ax.set_ylabel("% of same weekday in 2019")
    ax.set_title("Monday is weakest every year — but slowly catching up")
    ax.set_ylim(0, 100)
    ax.legend(ncol=5, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

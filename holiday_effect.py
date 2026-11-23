#!/usr/bin/env python3
"""Holiday effect: how quiet are the fixed-date holidays?

day_type 'U' mixes Sundays and holidays, so this isolates fixed calendar
dates (Christmas, New Year's Day, July 4, New Year's Eve) and compares
their average daily rides with a normal 2019 Sunday and a normal 2019
weekday. Thanksgiving is excluded: its date moves year to year.

Run: python3 holiday_effect.py  (reads data/ridership.sqlite, writes
charts/holiday_effect.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "holiday_effect.png")
DATES = [("Christmas Day", "12-25"), ("New Year's Day", "01-01"),
         ("July 4", "07-04"), ("New Year's Eve", "12-31")]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, total_rides, day_type FROM ridership"
    ).fetchall()
    con.close()
    labels, vals = [], []
    for name, md in DATES:
        sel = [t for d, t, _ in rows
               if d[5:] == md and int(d[:4]) >= 2019]
        labels.append(name)
        vals.append(sum(sel) / len(sel))
        print(f"{name}: {sum(sel) / len(sel):,.0f} avg rides (n={len(sel)})")
    sun19 = sum(t for d, t, dt in rows
                if dt == "U" and d.startswith("2019")) / sum(
                    1 for d, t, dt in rows if dt == "U" and d.startswith("2019"))
    wd19 = sum(t for d, t, dt in rows
               if dt == "W" and d.startswith("2019")) / sum(
                   1 for d, t, dt in rows if dt == "W" and d.startswith("2019"))
    print(f"2019 Sunday avg: {sun19:,.0f}; 2019 weekday avg: {wd19:,.0f}")
    print(f"Christmas Day vs 2019 Sunday: {vals[0] / sun19 * 100:.0f}%")

    fig, ax = plt.subplots()
    ax.bar(labels, [v / 1000 for v in vals])
    ax.axhline(sun19 / 1000, color="tab:orange", linestyle="--",
               label="2019 Sunday avg (634k)")
    ax.axhline(wd19 / 1000, color="tab:green", linestyle="--",
               label="2019 weekday avg (1,469k)")
    ax.set_ylabel("Average daily rides (thousands)")
    ax.set_title("Fixed-date holidays: Christmas Day is the quietest")
    ax.legend(fontsize=8)
    for i, v in enumerate(vals):
        ax.text(i, v / 1000 + 30, f"{v / 1000:.0f}k", ha="center")
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

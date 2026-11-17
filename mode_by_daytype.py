#!/usr/bin/env python3
"""Bus vs rail recovery by day type: is the rail lag a weekday-only story?

The shipped bus-vs-rail chart is monthly overall. Cross-tabulating mode
by day_type (W/A/U) over the latest 12 months vs 2019 shows whether rail
lags everywhere or mainly on weekdays.

Run: python3 mode_by_daytype.py  (reads data/ridership.sqlite, writes
charts/mode_by_daytype.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "mode_by_daytype.png")
LABELS = {"W": "Weekday", "A": "Saturday", "U": "Sun/Holiday"}


def avg(rows, col):
    return sum(r[col] for r in rows) / len(rows) if rows else 0


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, day_type, bus, rail_boardings, total_rides "
        "FROM ridership"
    ).fetchall()
    con.close()
    cats, bus_pct, rail_pct = [], [], []
    for dt in ["W", "A", "U"]:
        for col, store in [(2, bus_pct), (3, rail_pct)]:
            b = [r for r in rows if r[0].startswith("2019") and r[1] == dt]
            r = [r for r in rows if "2025-09-01" <= r[0] <= "2026-08-31"
                 and r[1] == dt]
            store.append(100 * avg(r, col) / avg(b, col))
        cats.append(LABELS[dt])
        print(f"{LABELS[dt]}: bus {bus_pct[-1]:.1f}% of 2019, "
              f"rail {rail_pct[-1]:.1f}% of 2019")
    x = range(len(cats))
    fig, ax = plt.subplots()
    ax.bar([i - 0.2 for i in x], bus_pct, width=0.4, label="Bus")
    ax.bar([i + 0.2 for i in x], rail_pct, width=0.4, label="Rail")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats)
    ax.set_ylabel("% of 2019 average")
    ax.set_title("Recovery by mode and day type (latest 12 months vs 2019)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

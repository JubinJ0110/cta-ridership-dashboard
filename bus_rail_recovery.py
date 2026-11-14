#!/usr/bin/env python3
"""Bus vs rail monthly recovery: each mode as a % of the same month in 2019.

Tests whether rail is closing the gap with bus. Monthly values are
noisy (weather, holidays), so the writeup in stdout also reports the
latest 12 months as a single % for each mode.

Run: python3 bus_rail_recovery.py  (reads data/ridership.sqlite, writes
charts/bus_vs_rail_recovery.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "bus_vs_rail_recovery.png")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               CAST(strftime('%m', service_date) AS INTEGER) AS m,
               SUM(bus) AS bus, SUM(rail_boardings) AS rail
        FROM ridership
        GROUP BY y, m ORDER BY y, m
        """
    ).fetchall()
    con.close()
    base = {(y, m): (b, r) for y, m, b, r in rows if y == 2019}
    months, bus_pct, rail_pct = [], [], []
    for y, m, b, r in rows:
        if y < 2022 or (y, m) not in base:
            continue
        bb, rb = base[(y, m)]
        months.append(f"{y}-{m:02d}")
        bus_pct.append(100 * b / bb)
        rail_pct.append(100 * r / rb)
    # Latest 12 months in the data, as one % per mode.
    latest = rows[-12:]
    lb = sum(b for _, _, b, _ in latest)
    lr = sum(r for _, _, _, r in latest)
    # Same 12 calendar months in 2019.
    base12 = [base[(2019, m)] for _, m, _, _ in latest]
    print(f"latest 12 months: bus {100*lb/sum(b for b, _ in base12):.1f}% of 2019, "
          f"rail {100*lr/sum(r for _, r in base12):.1f}% of 2019")

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(months, bus_pct, label="Bus (% of same month 2019)")
    ax.plot(months, rail_pct, label="Rail (% of same month 2019)")
    ax.axhline(100, color="grey", linestyle=":", linewidth=1)
    ax.set_title("Bus vs rail recovery: % of the same month in 2019")
    ax.set_xlabel("Month")
    ax.set_ylabel("% of 2019")
    ax.set_xticks(range(0, len(months), 6))
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

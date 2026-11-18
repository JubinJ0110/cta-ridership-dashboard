#!/usr/bin/env python3
"""Recovery deceleration: year-over-year growth is shrinking.

The shipped forecast extrapolates the 2021-2025 trend to 2029. This
checks that trend directly: yearly growth rates plus monthly YoY for
2025 vs 2024 and 2026 vs 2025 (Jan-Aug, the data available for 2026).

Run: python3 growth_deceleration.py  (reads data/ridership.sqlite, writes
charts/growth_deceleration.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "growth_deceleration.png")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, total_rides FROM ridership"
    ).fetchall()
    con.close()
    yearly = {}
    for y in range(2019, 2027):
        yearly[y] = sum(t for d, t in rows if d.startswith(str(y)))
    for y in range(2021, 2026):
        print(f"{y}: {(yearly[y] / yearly[y - 1] - 1) * 100:+.1f}% YoY "
              f"({yearly[y] / 1e6:.1f}M rides)")
    ja = {y: sum(t for d, t in rows
                 if d.startswith(str(y)) and int(d[5:7]) <= 8)
          for y in (2024, 2025, 2026)}
    print(f"Jan-Aug 2026 vs 2025: {(ja[2026] / ja[2025] - 1) * 100:+.1f}% "
          f"({ja[2026] / 1e6:.1f}M vs {ja[2025] / 1e6:.1f}M)")
    for m in range(1, 9):
        def mt(y, mm):
            return sum(t for d, t in rows if d.startswith(f"{y}-{mm:02d}"))
        print(f"  month {m:02d}: 2026 vs 2025 "
              f"{(mt(2026, m) / mt(2025, m) - 1) * 100:+.1f}%")
    years = [2021, 2022, 2023, 2024, 2025]
    growth = [100 * (yearly[y] / yearly[y - 1] - 1) for y in years]
    fig, ax = plt.subplots()
    ax.bar([str(y) for y in years], growth)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Year-over-year growth (%)")
    ax.set_title("Ridership YoY growth is shrinking (2021-2025)")
    for i, v in enumerate(growth):
        ax.text(i, v + 0.8, f"{v:+.1f}%", ha="center")
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

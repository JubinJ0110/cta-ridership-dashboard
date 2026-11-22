#!/usr/bin/env python3
"""Recovery by calendar month: which months are closest to 2019?

Monthly totals for 2025 and Jan-Sep 2026 as % of the same month in 2019.
2019 and 2025 are both non-leap years, so same-month totals are directly
comparable (same number of days).

Run: python3 monthly_recovery.py  (reads data/ridership.sqlite, writes
charts/monthly_recovery.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "monthly_recovery.png")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, total_rides FROM ridership").fetchall()
    con.close()

    def mt(y, m):
        return sum(t for d, t in rows if d.startswith(f"{y}-{m:02d}"))

    rec25 = [100 * mt(2025, m) / mt(2019, m) for m in range(1, 13)]
    rec26 = [100 * mt(2026, m) / mt(2019, m) if mt(2026, m) else None
             for m in range(1, 13)]
    for i, m in enumerate(MONTHS):
        extra = f", 2026: {rec26[i]:.1f}%" if rec26[i] else ""
        print(f"{m}: 2025 {rec25[i]:.1f}% of 2019{extra}")
    print(f"Strongest 2025 month: {MONTHS[rec25.index(max(rec25))]} "
          f"{max(rec25):.1f}%; weakest: {MONTHS[rec25.index(min(rec25))]} "
          f"{min(rec25):.1f}%")

    fig, ax = plt.subplots()
    x = list(range(12))
    ax.bar(x, rec25, label="2025 vs 2019")
    xs26 = [i for i, v in enumerate(rec26) if v is not None]
    ax.plot(xs26, [rec26[i] for i in xs26], "o-", color="tab:orange",
            label="2026 vs 2019 (Jan-Sep)")
    ax.set_xticks(x)
    ax.set_xticklabels(MONTHS)
    ax.set_ylabel("% of same month in 2019")
    ax.set_title("Recovery by calendar month: summer leads, winter lags")
    ax.set_ylim(0, 100)
    ax.legend()
    for i, v in enumerate(rec25):
        ax.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

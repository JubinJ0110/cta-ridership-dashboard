#!/usr/bin/env python3
"""2026 pace tracker: is this year beating last year, and where does it land?

Monthly totals for Jan-Sep 2026 vs the same months in 2019 and 2025,
plus a full-year 2026 projection using the record_days.py method:
Jan-Sep 2026 pace vs Jan-Sep 2025, scaled by the full 2025 total.
2019 and 2025 are both non-leap years, so same-month totals are directly
comparable (same number of days); 2026 is also a non-leap year.

Run: python3 pace_tracker.py  (reads data/ridership.sqlite, writes
charts/pace_tracker_2026.png)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
OUT = os.path.join(HERE, "charts", "pace_tracker_2026.png")
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep"]


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT service_date, total_rides FROM ridership").fetchall()
    con.close()

    def mt(y, m1=1, m2=12):
        return sum(t for d, t in rows
                   if d.startswith(str(y)) and m1 <= int(d[5:7]) <= m2)

    months = [m for m in range(1, 13) if mt(2026, m, m) > 0]
    tot19 = [mt(2019, m, m) / 1e6 for m in months]
    tot25 = [mt(2025, m, m) / 1e6 for m in months]
    tot26 = [mt(2026, m, m) / 1e6 for m in months]
    for i, m in enumerate(months):
        print(f"{MONTHS[m - 1]}: 2026 {tot26[i]:.1f}M vs 2019 "
              f"{tot19[i]:.1f}M ({100 * tot26[i] / tot19[i]:.1f}%), "
              f"vs 2025 {tot25[i]:.1f}M ({100 * (tot26[i] / tot25[i] - 1):+.1f}%)")
    js26, js25, js19 = mt(2026, 1, 9), mt(2025, 1, 9), mt(2019, 1, 9)
    fy25, fy19 = mt(2025), mt(2019)
    proj = js26 / js25 * fy25
    print(f"Jan-Sep 2026: {js26 / 1e6:.1f}M "
          f"({100 * (js26 / js25 - 1):+.1f}% vs 2025, "
          f"{100 * js26 / js19:.1f}% of 2019)")
    print(f"2026 projection: {proj / 1e6:.1f}M rides "
          f"({100 * proj / fy19:.1f}% of 2019)")

    x = list(range(len(months)))
    w = 0.25
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - w for i in x], tot19, width=w, label="2019",
           color="tab:gray")
    ax.bar(x, tot25, width=w, label="2025", color="tab:blue")
    ax.bar([i + w for i in x], tot26, width=w, label="2026",
           color="tab:orange")
    ax.set_xticks(x)
    ax.set_xticklabels([MONTHS[m - 1] for m in months])
    ax.set_ylabel("Monthly rides (millions)")
    ax.set_title("2026 pace tracker: ahead of 2025 every month so far")
    ax.text(0.01, 0.97,
            f"Jan-Sep 2026: {js26 / 1e6:.1f}M "
            f"({100 * (js26 / js25 - 1):+.1f}% vs 2025, "
            f"{100 * js26 / js19:.1f}% of 2019)\n"
            f"Full-year projection: {proj / 1e6:.1f}M "
            f"({100 * proj / fy19:.1f}% of 2019)",
            transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      alpha=0.85))
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax.set_ylim(0, max(tot19) * 1.15)
    fig.tight_layout()
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

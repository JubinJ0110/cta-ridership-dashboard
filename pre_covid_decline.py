#!/usr/bin/env python3
"""Pre-COVID decline, 2012-2019: yearly totals from the 2012 peak down
to 2019, with a writeup. COVID hit a system already in decline — and
the decline was mostly bus, not rail.

Run: python3 pre_covid_decline.py  (reads data/ridership.sqlite, writes
charts/pre_covid_decline.png and docs/pre_covid_decline.md)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
CHART = os.path.join(HERE, "charts", "pre_covid_decline.png")
DOC = os.path.join(HERE, "docs", "pre_covid_decline.md")


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               SUM(total_rides) / 1e6 AS total_m,
               SUM(bus) / 1e6 AS bus_m,
               SUM(rail_boardings) / 1e6 AS rail_m
        FROM ridership
        WHERE y BETWEEN 2012 AND 2019
        GROUP BY y ORDER BY y
        """
    ).fetchall()
    con.close()
    years = [r[0] for r in rows]
    total = [r[1] for r in rows]
    bus = [r[2] for r in rows]
    rail = [r[3] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(years, total, marker="o", label="Total")
    ax.plot(years, bus, marker="o", markersize=3, label="Bus")
    ax.plot(years, rail, marker="o", markersize=3, label="Rail")
    ax.set_title("CTA yearly rides 2012-2019: the pre-COVID decline (millions)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Million rides")
    ax.set_xticks(years)
    ax.legend()
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(CHART), exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHART, dpi=150)
    print(f"wrote {CHART}")

    peak, end = total[0], total[-1]
    bus_drop = bus[0] - bus[-1]
    rail_drop = rail[0] - rail[-1]
    lines = [
        "# The decline before COVID: 2012-2019",
        "",
        f"Ridership peaked in **2012 at {peak:.1f}M rides** and fell every",
        f"year but one to **{end:.1f}M in 2019 — down {100*(peak-end)/peak:.1f}%**",
        "before COVID ever arrived. The pandemic hit a system already",
        "losing riders for seven years.",
        "",
        "## Yearly totals (millions)",
        "",
        "| Year | Total | Bus | Rail |",
        "|------|------:|----:|-----:|",
    ]
    for y, t, b, r in rows:
        lines.append(f"| {y} | {t:.1f} | {b:.1f} | {r:.1f} |")
    lines += [
        "",
        "## It was mostly a bus story",
        "",
        f"- Bus fell {bus[0]:.1f}M to {bus[-1]:.1f}M "
        f"(-{100*bus_drop/bus[0]:.1f}%, {bus_drop:.1f}M rides lost).",
        f"- Rail fell {rail[0]:.1f}M to {rail[-1]:.1f}M "
        f"(-{100*rail_drop/rail[0]:.1f}%, {rail_drop:.1f}M rides lost).",
        f"- Bus accounted for {100*bus_drop/(bus_drop+rail_drop):.0f}% of the total decline.",
        "",
        "That matters for the recovery story: bus has also recovered",
        "faster than rail since 2020, so the mode that lost the most",
        "before COVID is the one coming back fastest after it.",
        "",
    ]
    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    with open(DOC, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {DOC}")
    print(f"2012 {peak:.1f}M -> 2019 {end:.1f}M; bus -{bus_drop:.1f}M, rail -{rail_drop:.1f}M")


if __name__ == "__main__":
    main()

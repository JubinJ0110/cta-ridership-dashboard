#!/usr/bin/env python3
"""Forecast: simple projection of when ridership gets back to 2019 levels.

Method: ordinary least-squares trend on full-year totals 2021-2025
(the post-trough recovery years), extrapolated forward. This is a
trend extrapolation, NOT a prediction: it assumes the 2021-2025 pace
holds, ignores fare/service/policy changes, and the 2026 total is
still partial (Jan-Aug only, so it is excluded from the fit).

Run: python3 forecast.py  (reads data/ridership.sqlite, writes
charts/forecast.png and docs/forecast.md)
"""
import os
import sqlite3

import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "data", "ridership.sqlite")
CHART = os.path.join(HERE, "charts", "forecast.png")
DOC = os.path.join(HERE, "docs", "forecast.md")
FIT_YEARS = [2021, 2022, 2023, 2024, 2025]


def linfit(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum(
        (x - mx) ** 2 for x in xs
    )
    return slope, my - slope * mx


def main():
    con = sqlite3.connect(DB)
    rows = con.execute(
        """
        SELECT CAST(strftime('%Y', service_date) AS INTEGER) AS y,
               SUM(total_rides) / 1e6 AS rides_m
        FROM ridership
        GROUP BY y ORDER BY y
        """
    ).fetchall()
    con.close()
    totals = dict(rows)
    baseline_2019 = totals[2019]
    fit = [(y, totals[y]) for y in FIT_YEARS]
    slope, intercept = linfit([y for y, _ in fit], [v for _, v in fit])
    projected = {}
    year = 2026
    while year <= 2035:
        projected[year] = slope * year + intercept
        year += 1
    crossing = next(
        (y for y, v in projected.items() if v >= baseline_2019), None
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    xs = sorted(totals)
    ax.plot(xs, [totals[y] for y in xs], marker="o", markersize=3,
            label="Actual (2001-2026 partial)")
    px = sorted(projected)
    ax.plot(px, [projected[y] for y in px], linestyle="--", marker="",
            label="Trend extrapolation (2021-2025 fit)")
    ax.axhline(baseline_2019, color="grey", linestyle=":", linewidth=1,
               label=f"2019 level ({baseline_2019:.1f}M)")
    ax.set_title("CTA yearly rides: actual vs trend extrapolation (millions)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Million rides")
    ax.legend()
    ax.grid(alpha=0.3)
    os.makedirs(os.path.dirname(CHART), exist_ok=True)
    fig.tight_layout()
    fig.savefig(CHART, dpi=150)
    print(f"wrote {CHART}")

    os.makedirs(os.path.dirname(DOC), exist_ok=True)
    lines = [
        "# When does ridership get back to 2019 levels?",
        "",
        "**Trend extrapolation, not a prediction.** A straight line fitted",
        "to full-year totals 2021-2025 (the post-trough recovery) and",
        "extended forward. It assumes that pace holds and ignores fare,",
        "service, and policy changes. 2026 is excluded from the fit",
        "(Jan-Aug only).",
        "",
        "## Fitted trend",
        "",
        f"- 2019 baseline: **{baseline_2019:.1f}M rides**",
        f"- Recovery pace: **+{slope:.1f}M rides per year** (2021-2025 fit)",
        f"- Projected return to 2019 level: **{crossing}**"
        if crossing else "- No return to 2019 level projected by 2035",
        "",
        "## Projected yearly totals (millions)",
        "",
        "| Year | Projected |",
        "|------|----------:|",
    ]
    for y in sorted(projected):
        if y <= (crossing or 2030):
            lines.append(f"| {y} | {projected[y]:.1f} |")
    lines += [
        "",
        "## Why this could be wrong",
        "",
        "- Growth has already slowed: yearly gains were +47.6M (2022),",
        "  +35.6M (2023), +30.1M (2024), +28.8M (2025). A straight line",
        "  ignores that deceleration, so the crossing year is optimistic",
        "  if growth keeps slowing.",
        "- Weekday commuting (the weakest segment) depends on remote-work",
        "  patterns, which a trend line cannot see.",
        "",
    ]
    with open(DOC, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {DOC}")
    print(f"pace +{slope:.1f}M/yr, crossing {crossing}")


if __name__ == "__main__":
    main()

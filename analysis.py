#!/usr/bin/env python3
"""Analyze CTA daily ridership from the local SQLite database and save charts.

Reads data/ridership.sqlite (created by fetch_ridership.py), prints headline
stats, and writes PNG charts into charts/:
  1. yearly_total_rides.png — total rides per year, 2001 to present
  2. bus_vs_rail_share.png — bus vs rail share of total rides by year
  3. monthly_rides_2019_present.png — monthly totals from 2019 on, showing
     the COVID drop and the recovery

Usage:
    python3 fetch_ridership.py   # first, to build/update the database
    python3 analysis.py
"""

import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "ridership.sqlite"
CHARTS_DIR = BASE_DIR / "charts"

MILLIONS = 1_000_000


def load_yearly(conn):
    rows = conn.execute(
        """
        SELECT
            substr(service_date, 1, 4) AS year,
            SUM(total_rides) AS total,
            SUM(bus) AS bus,
            SUM(rail_boardings) AS rail,
            COUNT(*) AS days
        FROM ridership
        GROUP BY year
        ORDER BY year
        """
    ).fetchall()
    return rows


def load_monthly(conn, start="2019-01-01"):
    return conn.execute(
        """
        SELECT substr(service_date, 1, 7) AS month, SUM(total_rides) AS total
        FROM ridership
        WHERE service_date >= ?
        GROUP BY month
        ORDER BY month
        """,
        (start,),
    ).fetchall()


def fmt_millions(value):
    return f"{value / MILLIONS:.1f}M"


def main():
    if not DB_PATH.exists():
        print(f"No database found at {DB_PATH}. Run fetch_ridership.py first.")
        raise SystemExit(1)

    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    yearly = load_yearly(conn)
    years = [int(r[0]) for r in yearly]
    totals = [r[1] for r in yearly]
    bus = [r[2] for r in yearly]
    rail = [r[3] for r in yearly]
    days = {int(r[0]): r[4] for r in yearly}
    by_year = {int(r[0]): r for r in yearly}

    def total(year):
        return by_year[year][1] if year in by_year else None

    print("=== CTA daily ridership — headline stats ===")
    print(f"Coverage: {years[0]}–{years[-1]} ({sum(days.values()):,} days)")
    print()

    print("Yearly totals (millions of rides):")
    for y in (2019, 2020, 2021, 2022, 2023, 2024, 2025):
        if y in by_year:
            print(f"  {y}: {fmt_millions(total(y))} ({days[y]} days)")
    print()

    for base, comp in ((2019, 2023), (2019, 2024), (2019, 2025)):
        if base in by_year and comp in by_year:
            change = (total(comp) / total(base) - 1) * 100
            print(f"{comp} vs {base}: {change:+.1f}% ({fmt_millions(total(comp))} vs {fmt_millions(total(base))})")
    print()

    print("Bus vs rail share of total rides:")
    for y in (2019, 2020, 2023, 2024, 2025):
        if y in by_year:
            t, b, r = total(y), by_year[y][2], by_year[y][3]
            print(f"  {y}: bus {b / t * 100:.1f}%, rail {r / t * 100:.1f}%")
    print()

    # COVID trough: worst month by total rides since 2020.
    monthly = load_monthly(conn, "2019-01-01")
    trough_month, trough_total = min(monthly, key=lambda m: m[1])
    peak_2019 = max((m for m in monthly if m[0].startswith("2019")), key=lambda m: m[1])
    print(f"COVID trough month: {trough_month} — {fmt_millions(trough_total)} rides")
    print(
        f"Best 2019 month for comparison: {peak_2019[0]} — "
        f"{fmt_millions(peak_2019[1])} rides"
    )
    print(
        f"Trough was {trough_total / peak_2019[1] * 100:.1f}% of the best 2019 month."
    )
    print()

    # Weekday vs weekend averages, 2019 vs latest full year.
    for label, year in (("2019", 2019), ("2024", 2024)):
        rows = conn.execute(
            """
            SELECT day_type, AVG(total_rides) FROM ridership
            WHERE substr(service_date, 1, 4) = ?
            GROUP BY day_type
            """,
            (str(year),),
        ).fetchall()
        avgs = dict(rows)
        print(
            f"{label} daily average — weekday (W): {avgs.get('W', 0):,.0f}, "
            f"Saturday (A): {avgs.get('A', 0):,.0f}, "
            f"Sunday/holiday (U): {avgs.get('U', 0):,.0f}"
        )
    print()

    # Latest 12 months vs 2019 baseline.
    last_month = monthly[-1][0]
    last12 = monthly[-12:]
    last12_total = sum(m[1] for m in last12)
    months_2019 = [m for m in monthly if m[0].startswith("2019")]
    total_2019 = sum(m[1] for m in months_2019)
    print(
        f"Latest 12 months ({last12[0][0]} to {last_month}): "
        f"{fmt_millions(last12_total)} rides"
    )
    print(
        f"Same span vs 2019 total ({fmt_millions(total_2019)}): "
        f"{last12_total / total_2019 * 100:.1f}% of 2019"
    )
    conn.close()

    # --- Charts ---
    plt.rcParams.update({"figure.figsize": (10, 5.5), "axes.grid": True})

    # 1. Yearly total rides.
    fig, ax = plt.subplots()
    ax.bar(years, [t / MILLIONS for t in totals], color="#1f77b4")
    ax.set_title("CTA total rides per year (bus + rail)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Millions of rides")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}M"))
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "yearly_total_rides.png", dpi=150)
    plt.close(fig)

    # 2. Bus vs rail share over time.
    bus_share = [b / t * 100 for b, t in zip(bus, totals)]
    rail_share = [r / t * 100 for r, t in zip(rail, totals)]
    fig, ax = plt.subplots()
    ax.plot(years, bus_share, marker="o", label="Bus share (%)")
    ax.plot(years, rail_share, marker="o", label="Rail share (%)")
    ax.set_title("Bus vs rail share of CTA rides by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Share of total rides (%)")
    ax.set_ylim(0, 100)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "bus_vs_rail_share.png", dpi=150)
    plt.close(fig)

    # 3. Monthly totals 2019 to present.
    months = [m[0] for m in monthly]
    month_totals = [m[1] / MILLIONS for m in monthly]
    fig, ax = plt.subplots()
    ax.plot(months, month_totals, color="#1f77b4")
    ax.fill_between(months, month_totals, alpha=0.15, color="#1f77b4")
    ax.set_title("CTA total rides per month, 2019 to present")
    ax.set_xlabel("Month")
    ax.set_ylabel("Millions of rides")
    ax.tick_params(axis="x", labelrotation=45)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(14))
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "monthly_rides_2019_present.png", dpi=150)
    plt.close(fig)

    print("Charts saved to charts/:")
    for name in (
        "yearly_total_rides.png",
        "bus_vs_rail_share.png",
        "monthly_rides_2019_present.png",
    ):
        print(f"  charts/{name}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Scheduled-service baseline: how much service does CTA run?

Downloads the current CTA GTFS static feed (keyless public ZIP) and counts
scheduled trips and service-hours per day type, bus vs rail. This is the
SCHEDULED side only: the actuals side needs a free Bus Tracker / Train
Tracker API key (see docs/service_baseline.md), which Jubin has not
provided — so nothing here claims to measure service actually delivered.

Method: a trip counts toward every day its service runs (calendar.txt).
Weekday = average over Mon-Fri; Saturday and Sunday are single days.
calendar_dates.txt exceptions (170 rows) are NOT applied — this is the
regular weekly pattern, not a specific date. Trip duration = last arrival
minus first departure in stop_times.txt.

Run: python3 service_baseline.py  (downloads the GTFS ZIP to a temp dir,
writes charts/service_baseline.png)
"""
import csv
import io
import os
import tempfile
import zipfile

import matplotlib.pyplot as plt
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "charts", "service_baseline.png")
GTFS_URL = ("https://www.transitchicago.com/downloads/sch_data/"
            "google_transit.zip")
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday",
        "saturday", "sunday"]
LABELS = ["Weekday\n(avg)", "Saturday", "Sunday"]


def secs(s):
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + int(sec)


def main():
    print(f"downloading {GTFS_URL}")
    r = requests.get(GTFS_URL, timeout=180,
                     headers={"User-Agent": "cta-ridership-dashboard"})
    r.raise_for_status()
    print(f"downloaded {len(r.content) / 1e6:.1f} MB")
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "google_transit.zip")
        with open(path, "wb") as f:
            f.write(r.content)
        z = zipfile.ZipFile(path)

        def rows(name):
            return csv.DictReader(
                io.TextIOWrapper(z.open(name), encoding="utf-8-sig"))

        routes = {row["route_id"]: row["route_type"]
                  for row in rows("routes.txt")}
        n_bus = sum(1 for t in routes.values() if t == "3")
        n_rail = sum(1 for t in routes.values() if t == "1")
        cal = {c["service_id"]: c for c in rows("calendar.txt")}
        start = min(c["start_date"] for c in cal.values())
        end = max(c["end_date"] for c in cal.values())
        print(f"feed covers {start} to {end}; "
              f"{n_bus} bus routes, {n_rail} rail routes")

        first, last = {}, {}
        with z.open("stop_times.txt") as f:
            for row in csv.DictReader(
                    io.TextIOWrapper(f, encoding="utf-8-sig")):
                tid = row["trip_id"]
                a, d = secs(row["arrival_time"]), secs(row["departure_time"])
                if tid not in first or d < first[tid]:
                    first[tid] = d
                if tid not in last or a > last[tid]:
                    last[tid] = a
        dur = {tid: (last[tid] - first[tid]) / 3600 for tid in first}

        trips = {d: {"bus": 0, "rail": 0} for d in DAYS}
        hours = {d: {"bus": 0.0, "rail": 0.0} for d in DAYS}
        for t in rows("trips.txt"):
            rt = "rail" if routes[t["route_id"]] == "1" else "bus"
            c = cal[t["service_id"]]
            h = dur[t["trip_id"]]
            for d in DAYS:
                if c[d] == "1":
                    trips[d][rt] += 1
                    hours[d][rt] += h

    def day_avg(table, key):
        return sum(table[d][key] for d in DAYS[:5]) / 5

    def fmt(yyyymmdd):
        import datetime
        return datetime.datetime.strptime(yyyymmdd, "%Y%m%d").strftime(
            "%b %d, %Y")

    cats = ["Weekday", "Saturday", "Sunday"]
    trip_bus = [day_avg(trips, "bus"), trips["saturday"]["bus"],
                trips["sunday"]["bus"]]
    trip_rail = [day_avg(trips, "rail"), trips["saturday"]["rail"],
                 trips["sunday"]["rail"]]
    hr_bus = [day_avg(hours, "bus"), hours["saturday"]["bus"],
              hours["sunday"]["bus"]]
    hr_rail = [day_avg(hours, "rail"), hours["saturday"]["rail"],
               hours["sunday"]["rail"]]
    for i, c in enumerate(cats):
        print(f"{c}: {trip_bus[i] + trip_rail[i]:,.0f} trips/day "
              f"(bus {trip_bus[i]:,.0f}, rail {trip_rail[i]:,.0f}); "
              f"{hr_bus[i] + hr_rail[i]:,.0f} service-hours "
              f"(bus {hr_bus[i]:,.0f}, rail {hr_rail[i]:,.0f})")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    x = list(range(3))
    w = 0.35
    ax1.bar([i - w / 2 for i in x], trip_bus, width=w, label="Bus")
    ax1.bar([i + w / 2 for i in x], trip_rail, width=w, label="Rail")
    ax1.set_xticks(x)
    ax1.set_xticklabels(LABELS)
    ax1.set_ylabel("Scheduled trips per day")
    ax1.set_title("Scheduled trips by day type")
    ax1.legend()
    ax2.bar([i - w / 2 for i in x], hr_bus, width=w, label="Bus")
    ax2.bar([i + w / 2 for i in x], hr_rail, width=w, label="Rail")
    ax2.set_xticks(x)
    ax2.set_xticklabels(LABELS)
    ax2.set_ylabel("Service-hours per day")
    ax2.set_title("Scheduled service-hours by day type")
    ax2.legend()
    fig.suptitle(f"Scheduled service baseline — GTFS feed "
                 f"{fmt(start)} to {fmt(end)}\n"
                 "Scheduled only: actual service not measured (needs API key)",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(OUT, dpi=150)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

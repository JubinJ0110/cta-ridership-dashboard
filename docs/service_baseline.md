# Service data — scheduled baseline, and what the actuals side needs

## What item 20 is

The first honest slice of the scheduled-vs-actual question: a baseline of
**scheduled** CTA service, built from the public GTFS static feed. It does
NOT measure service actually delivered — no actuals source is available
without an API key (below), so nothing here claims a scheduled-vs-actual
comparison.

## The baseline (from the feed fetched 2026-11-23)

- Source: CTA GTFS static feed, keyless public ZIP —
  https://www.transitchicago.com/downloads/sch_data/google_transit.zip
  (51.4 MB; feed covers 2026-10-29 to 2026-12-31; 124 bus routes, 8 rail
  routes; 55,492 trips).
- Scheduled trips per day: weekday avg 23,018 (bus 19,289, rail 3,729),
  Saturday 17,340 (bus 14,130, rail 3,210), Sunday 15,056 (bus 12,094,
  rail 2,962). Bus is 83.8% of weekday trips.
- Scheduled service-hours per day: weekday avg 20,316 (bus 16,598, rail
  3,717), Saturday 15,134, Sunday 12,584.
  weekday is the Mon–Fri average. The 170 calendar_dates.txt exceptions
  are NOT applied — this is the regular weekly pattern. Trip duration =
  last arrival minus first departure in stop_times.txt.
- The script re-downloads the feed on every run, so re-running it later
  measures the then-current schedule, not this snapshot.

## What is missing for the actuals side

Every real-time CTA feed needs a free API key, and no key is on file:

- **GTFS-Realtime** (Trip Updates + Vehicle Positions + Service Alerts)
  — https://transitdata.transitchicago.com/ — "An API key is required".
  This is the feed a true scheduled-vs-actual comparison would use:
  poll Vehicle Positions / Trip Updates, match each active trip to its
  scheduled trip, and report % of scheduled trips operated and on-time.
- **Bus Tracker API v2** — free key; sign in to a Bus Tracker account
  and request a Developer Key under "My Account"
  (https://www.transitchicago.com/developers/bustracker/). 10,000
  requests/day by default.
- **Train Tracker API** — free key via the application form
  (https://www.transitchicago.com/developers/traintrackerapply/).
- **Customer Alerts API** needs no key, but it only carries alerts —
  not vehicle positions or trip updates, so it cannot measure actuals.

**Jubin's step:** request the Bus Tracker and Train Tracker keys (free,
arrive by email after a short registration). With a key in hand, the
next item can poll the GTFS-Realtime feeds for a sample week and build
the real comparison: scheduled trips vs trips actually operated, bus vs
rail, by day type.

## Why this still matters without actuals

The baseline alone answers the first half of the rail-lag question: rail
runs only 16.2% of weekday scheduled trips but carries 42.5% of
September 2026 rides — about 122 riders per scheduled rail trip vs about
32 per bus trip (September daily averages divided by weekday scheduled
trips), so a small rail service cut hits ridership harder. The
baseline also gives the denominator the actuals comparison will need.

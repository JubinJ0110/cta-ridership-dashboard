# Methodology

## Data source

All figures come from the Chicago Data Portal dataset
[CTA – Ridership – Daily Boarding Totals](https://data.cityofchicago.org/Transportation/CTA-Ridership-Daily-Boarding-Totals/6iiy-9s97)
(Socrata resource `6iiy-9s97`), pulled by `fetch_ridership.py` into a local
SQLite database. The dataset reports **systemwide boardings** for CTA bus and
rail service, dating back to 2001.

## Columns

| Column | Meaning |
|---|---|
| `service_date` | The service day |
| `day_type` | `W` = weekday, `A` = Saturday, `U` = Sunday / holiday |
| `bus` | Bus boardings that day |
| `rail_boardings` | Rail boardings that day |
| `total_rides` | Bus + rail boardings that day |

## How the numbers are computed

- Yearly and monthly totals are plain sums of `total_rides` (and of `bus` /
  `rail_boardings` for mode shares).
- Daily averages divide the summed boardings by the number of service days in
  the group, so a year with more Saturdays does not look busier than it is.
- Year-over-year comparisons use the same calendar months in each year.
- The "latest 12 months" window is the 12 most recent months present in the
  data, compared against the same 12 months in 2019.

## Caveats

- **The data lags.** As of November 2026 the dataset runs through
  August 2026 — roughly a two-month lag. The pipeline is incremental, so new
  months appear automatically when the portal publishes them.
- Boardings count rides, not riders: one person taking a bus and then a train
  counts twice, and transfers count as separate boardings.
- `day_type = U` mixes Sundays and holidays, so holiday weeks read lower
  than a plain Sunday would.
- Service changes (new lines, discontinued routes, fare changes) affect
  boardings and are not adjusted for here. Any finding is descriptive, not
  causal: this project shows what happened, not why.

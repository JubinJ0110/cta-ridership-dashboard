with monthly as (
    select
        date_trunc('month', service_date) as month,
        sum(total_rides) as total_rides,
        sum(bus) as bus,
        sum(rail_boardings) as rail_boardings
    from {{ ref('int_daily_totals') }}
    group by 1
),
with_prior_year as (
    select
        month,
        total_rides,
        bus,
        rail_boardings,
        lag(total_rides) over (
            partition by extract(month from month) order by month
        ) as total_rides_same_month_last_year,
        lag(bus) over (
            partition by extract(month from month) order by month
        ) as bus_same_month_last_year,
        lag(rail_boardings) over (
            partition by extract(month from month) order by month
        ) as rail_same_month_last_year
    from monthly
)
select
    month,
    total_rides,
    bus,
    rail_boardings,
    total_rides_same_month_last_year,
    total_rides - total_rides_same_month_last_year as total_rides_yoy_change,
    (total_rides - total_rides_same_month_last_year) * 100.0
        / nullif(total_rides_same_month_last_year, 0) as total_rides_yoy_pct,
    bus_same_month_last_year,
    rail_same_month_last_year
from with_prior_year
order by month

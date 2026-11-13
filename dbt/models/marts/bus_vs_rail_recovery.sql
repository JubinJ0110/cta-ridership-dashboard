with monthly as (
    select
        date_trunc('month', service_date) as month,
        sum(bus) as bus,
        sum(rail_boardings) as rail_boardings,
        sum(total_rides) as total_rides
    from {{ ref('int_daily_totals') }}
    group by 1
),
baseline as (
    select
        extract(month from month) as month_of_year,
        bus as bus_2019,
        rail_boardings as rail_2019,
        total_rides as total_2019
    from monthly
    where extract(year from month) = 2019
)
select
    m.month,
    m.bus,
    m.rail_boardings,
    m.total_rides,
    m.bus * 100.0 / nullif(b.bus_2019, 0) as bus_pct_of_2019,
    m.rail_boardings * 100.0 / nullif(b.rail_2019, 0) as rail_pct_of_2019,
    m.total_rides * 100.0 / nullif(b.total_2019, 0) as total_pct_of_2019
from monthly m
join baseline b
    on extract(month from m.month) = b.month_of_year
order by m.month

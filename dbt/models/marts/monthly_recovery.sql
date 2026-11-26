with monthly as (
    select
        date_trunc('month', service_date) as month,
        sum(total_rides) as total_rides
    from {{ ref('int_daily_totals') }}
    group by 1
),
baseline as (
    select
        extract(month from month) as month_of_year,
        total_rides as total_rides_2019
    from monthly
    where extract(year from month) = 2019
)
select
    m.month,
    m.total_rides,
    m.total_rides * 100.0 / nullif(b.total_rides_2019, 0) as total_pct_of_2019
from monthly m
join baseline b
    on extract(month from m.month) = b.month_of_year
order by m.month

select
    date_trunc('month', service_date) as month,
    sum(total_rides) as total_rides,
    sum(bus) as bus,
    sum(rail_boardings) as rail_boardings,
    avg(total_rides) as avg_daily_rides,
    count(*) as days_in_month
from {{ ref('int_daily_totals') }}
group by 1
order by 1

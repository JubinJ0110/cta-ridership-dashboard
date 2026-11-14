with max_date as (
    select max(service_date) as max_service_date
    from {{ ref('int_daily_totals') }}
),
weekdays as (
    select
        extract(dow from service_date) as weekday_num,
        case extract(dow from service_date)
            when 1 then 'Mon'
            when 2 then 'Tue'
            when 3 then 'Wed'
            when 4 then 'Thu'
            when 5 then 'Fri'
        end as weekday,
        service_date,
        total_rides
    from {{ ref('int_daily_totals') }}
    where day_type = 'W'
),
baseline_2019 as (
    select
        weekday_num,
        weekday,
        avg(total_rides) as avg_daily_rides_2019
    from weekdays
    where extract(year from service_date) = 2019
    group by 1, 2
),
latest_12m as (
    select
        weekday_num,
        weekday,
        avg(total_rides) as avg_daily_rides_latest_12m
    from weekdays, max_date
    where service_date > max_service_date - interval 12 month
    group by 1, 2
)
select
    b.weekday_num,
    b.weekday,
    b.avg_daily_rides_2019,
    l.avg_daily_rides_latest_12m,
    l.avg_daily_rides_latest_12m * 100.0 / nullif(b.avg_daily_rides_2019, 0) as pct_of_2019
from baseline_2019 b
join latest_12m l
    on b.weekday_num = l.weekday_num
order by b.weekday_num

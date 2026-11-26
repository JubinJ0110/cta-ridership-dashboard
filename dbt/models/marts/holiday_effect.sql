with holidays as (
    select * from (values
        ('Christmas Day', 12, 25),
        ('New Year''s Day', 1, 1),
        ('July 4', 7, 4),
        ('New Year''s Eve', 12, 31)
    ) as t (holiday, month_of_year, day_of_month)
),
holiday_avg as (
    select
        h.holiday,
        avg(i.total_rides) as avg_daily_rides,
        count(*) as days_counted
    from holidays h
    join {{ ref('int_daily_totals') }} i
        on extract(month from i.service_date) = h.month_of_year
        and extract(day from i.service_date) = h.day_of_month
        and extract(year from i.service_date) >= 2019
    group by 1
),
baselines as (
    select
        avg(case when day_type = 'U' then total_rides end)
            as sunday_avg_2019,
        avg(case when day_type = 'W' then total_rides end)
            as weekday_avg_2019
    from {{ ref('int_daily_totals') }}
    where extract(year from service_date) = 2019
)
select
    h.holiday,
    h.avg_daily_rides,
    h.days_counted,
    b.sunday_avg_2019,
    b.weekday_avg_2019,
    h.avg_daily_rides * 100.0 / nullif(b.sunday_avg_2019, 0)
        as pct_of_2019_sunday_avg,
    h.avg_daily_rides * 100.0 / nullif(b.weekday_avg_2019, 0)
        as pct_of_2019_weekday_avg
from holiday_avg h
cross join baselines b
order by h.avg_daily_rides

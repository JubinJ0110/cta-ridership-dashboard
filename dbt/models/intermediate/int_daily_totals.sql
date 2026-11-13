select
    service_date,
    day_type,
    bus,
    rail_boardings,
    total_rides,
    bus * 1.0 / nullif(total_rides, 0) as bus_share,
    rail_boardings * 1.0 / nullif(total_rides, 0) as rail_share,
    extract(year from service_date) as year,
    extract(month from service_date) as month
from {{ ref('stg_ridership') }}

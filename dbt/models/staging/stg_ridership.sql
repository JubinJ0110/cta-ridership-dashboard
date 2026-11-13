select
    cast(service_date as date) as service_date,
    day_type,
    bus,
    rail_boardings,
    total_rides
from {{ source('cta', 'ridership') }}

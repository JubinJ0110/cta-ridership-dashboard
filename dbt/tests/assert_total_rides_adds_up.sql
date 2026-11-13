-- Every row's total must equal bus + rail.
select *
from {{ ref('stg_ridership') }}
where total_rides != bus + rail_boardings

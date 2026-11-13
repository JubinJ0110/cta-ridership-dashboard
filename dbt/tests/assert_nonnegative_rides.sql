-- Boardings can never be negative.
select *
from {{ ref('stg_ridership') }}
where bus < 0 or rail_boardings < 0

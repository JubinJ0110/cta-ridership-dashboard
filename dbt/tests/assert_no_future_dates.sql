-- No service dates in the future; a bad fetch must fail loudly.
select *
from {{ ref('stg_ridership') }}
where service_date > current_date

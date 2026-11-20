select
    store_id,
    device_id,
    ping_ts,
    date_trunc('hour', ping_ts) as hour_ts,
    hour(ping_ts)               as hour_of_day,
    dist_m
from {{ source('raw', 'store_visits') }}
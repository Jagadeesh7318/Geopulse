select
    H3_POINT_TO_CELL_STRING(geo, 9) as h3_id,
    hour(ping_ts)                   as hour_of_day,
    count(distinct device_id)       as unique_devices
from {{ source('raw', 'raw_pings') }}
group by 1, 2
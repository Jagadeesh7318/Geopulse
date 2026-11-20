select
    store_id,
    hour_ts,
    hour_of_day,
    case
        when hour_of_day between 7 and 9   then 'morning_peak'
        when hour_of_day between 17 and 19 then 'evening_peak'
        else 'off_peak'
    end                       as traffic_bucket,
    count(distinct device_id) as unique_visitors,
    count(*)                  as ping_count
from {{ ref('stg_store_visits') }}
group by 1, 2, 3, 4
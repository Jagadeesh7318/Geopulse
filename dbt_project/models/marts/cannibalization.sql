with visitors as (
    select distinct store_id, device_id
    from {{ ref('stg_store_visits') }}
),
store_totals as (
    select store_id, count(*) as total_devices
    from visitors
    group by 1
),
pairs as (
    select a.store_id as store_a,
           b.store_id as store_b,
           count(*)   as shared_devices
    from visitors a
    join visitors b
      on a.device_id = b.device_id
     and a.store_id <> b.store_id
    group by 1, 2
)
select
    p.store_a,
    p.store_b,
    p.shared_devices,
    t.total_devices as store_a_devices,
    round(100 * p.shared_devices / t.total_devices, 2) as overlap_pct_of_store_a
from pairs p
join store_totals t on t.store_id = p.store_a
order by overlap_pct_of_store_a desc
with source as (
    select *
    from {{ source('raw', 'wallet_features') }}
)

select
    wallet_address,
    tx_count,
    total_value,
    avg_tx_value,
    wallet_lifetime_days,
    days_since_last_tx,
    tx_per_day,
    churned
from source

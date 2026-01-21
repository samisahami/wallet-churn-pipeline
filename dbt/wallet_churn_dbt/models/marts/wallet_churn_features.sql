{{ config(materialized='table') }}

select
  wallet_address,
  tx_count,
  total_value,
  avg_tx_value,
  wallet_lifetime_days,
  days_since_last_tx,
  tx_per_day,
  churned
from {{ ref('stg_wallet_features') }}

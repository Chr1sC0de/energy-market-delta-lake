# Gas Market Mart ERD

This document covers the currently implemented market and scheduling facts in
`silver.gas_model`.

## Table of contents

- [Fact Inventory](#fact-inventory)
- [ERD](#erd)
- [Implemented Source Tables](#implemented-source-tables)
- [Notes](#notes)
- [Related docs](#related-docs)

## Fact Inventory

| Asset | Grain |
| --- | --- |
| `silver.gas_model.silver_gas_fact_market_price` | one row per source-specific market price observation |
| `silver.gas_model.silver_gas_fact_schedule_run` | one row per source schedule run |
| `silver.gas_model.silver_gas_fact_scheduled_quantity` | one row per source-specific scheduled quantity observation |
| `silver.gas_model.silver_gas_fact_bid_stack` | one row per source-specific bid stack step |

## ERD

```mermaid
erDiagram
    SILVER_GAS_DIM_DATE ||--o{ SILVER_GAS_FACT_MARKET_PRICE : date_key
    SILVER_GAS_DIM_DATE ||--o{ SILVER_GAS_FACT_SCHEDULE_RUN : date_key
    SILVER_GAS_DIM_DATE ||--o{ SILVER_GAS_FACT_SCHEDULED_QUANTITY : date_key
    SILVER_GAS_DIM_DATE ||--o{ SILVER_GAS_FACT_BID_STACK : date_key
    SILVER_GAS_DIM_PARTICIPANT ||--o{ SILVER_GAS_FACT_BID_STACK : participant_key

    SILVER_GAS_FACT_MARKET_PRICE {
        string table_name "silver.gas_model.silver_gas_fact_market_price"
        string surrogate_key PK
        string date_key FK
        string source_system
        list source_tables
        string source_table
        date gas_date
        string price_type
        string schedule_type_id
        string schedule_interval
        string transmission_id
        string transmission_doc_id
        string source_location_id
        float price_value_gst_ex
        float weighted_average_price_gst_ex
        float cumulative_price
        float administered_price
        string source_surrogate_key
        string source_file
        timestamp ingested_timestamp
    }

    SILVER_GAS_FACT_SCHEDULE_RUN {
        string table_name "silver.gas_model.silver_gas_fact_schedule_run"
        string surrogate_key PK
        string date_key FK
        string source_system
        list source_tables
        string source_table
        date gas_date
        string transmission_id
        string transmission_document_id
        string transmission_group_id
        string schedule_type_id
        string forecast_demand_version
        string demand_type_id
        float objective_function_value
        timestamp gas_start_timestamp
        timestamp bid_cutoff_timestamp
        timestamp creation_timestamp
        timestamp approval_timestamp
        string source_surrogate_key
        string source_file
        timestamp ingested_timestamp
    }

    SILVER_GAS_FACT_SCHEDULED_QUANTITY {
        string table_name "silver.gas_model.silver_gas_fact_scheduled_quantity"
        string surrogate_key PK
        string date_key FK
        string source_system
        list source_tables
        string source_table
        date gas_date
        string quantity_type
        string schedule_type_id
        string transmission_id
        string transmission_doc_id
        string source_point_id
        float quantity_gj
        float volume_kscm
        float amount_gst_ex
        string source_surrogate_key
        string source_file
        timestamp ingested_timestamp
    }

    SILVER_GAS_FACT_BID_STACK {
        string table_name "silver.gas_model.silver_gas_fact_bid_stack"
        string surrogate_key PK
        string date_key FK
        string participant_key FK
        string source_system
        list source_tables
        string source_table
        date gas_date
        string participant_id
        string participant_name
        string source_point_id
        string bid_id
        int bid_step
        float bid_price
        float bid_qty_gj
        float step_qty_gj
        string offer_type
        string inject_withdraw
        string schedule_type
        string schedule_time
        timestamp bid_cutoff_timestamp
        string source_surrogate_key
        string source_file
        timestamp ingested_timestamp
    }
```

## Implemented Source Tables

- `silver_gas_fact_market_price`:
  `silver.vicgas.silver_int037b_v4_indicative_mkt_price_1`,
  `silver.vicgas.silver_int037c_v4_indicative_price_1`,
  `silver.vicgas.silver_int039b_v4_indicative_locational_price_1`,
  `silver.vicgas.silver_int041_v4_market_and_reference_prices_1`,
  `silver.vicgas.silver_int042_v4_weighted_average_daily_prices_1`,
  `silver.vicgas.silver_int199_v4_cumulative_price_1`,
  `silver.vicgas.silver_int310_v1_price_and_withdrawals_rpt_1`,
  `silver.vicgas.silver_int310_v4_price_and_withdrawals_1`,
  `silver.vicgas.silver_int235_v4_sched_system_total_1`
- `silver_gas_fact_schedule_run`:
  `silver.vicgas.silver_int108_v4_scheduled_run_log_7_1`
- `silver_gas_fact_scheduled_quantity`:
  `silver.vicgas.silver_int050_v4_sched_withdrawals_1`,
  `silver.vicgas.silver_int235_v4_sched_system_total_1`,
  `silver.vicgas.silver_int291_v4_out_of_merit_order_gas_1`,
  `silver.vicgas.silver_int316_v4_operational_gas_1`
- `silver_gas_fact_bid_stack`:
  `silver.vicgas.silver_int131_v4_bids_at_bid_cutoff_times_prev_2_1`,
  `silver.vicgas.silver_int314_v4_bid_stack_1`

## Notes

- `participant_key` on `silver_gas_fact_bid_stack` is currently nullable; the
  transform keeps source participant identifiers without resolving them to
  `silver_gas_dim_participant`.
- `silver_gas_fact_market_price` and `silver_gas_fact_scheduled_quantity` use
  source-qualified location, node, and transmission identifiers rather than
  conformed dimension foreign keys.

## Related docs

- [Gas-model index](README.md)
- [Shared dimensions ERD](gas_dim_erd.md)
- [High-level architecture](../architecture/high_level_architecture.md)
- [Ingestion sequence diagrams](../architecture/ingestion_flows.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_market_price.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_schedule_run.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_scheduled_quantity.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_bid_stack.py`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`

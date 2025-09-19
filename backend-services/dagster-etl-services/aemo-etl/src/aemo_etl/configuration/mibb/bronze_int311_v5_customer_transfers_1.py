from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int311_v5_customer_transfers_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int311_v5_customer_transfers_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "transfers_lodged": Int64,
    "transfers_completed": Int64,
    "transfers_cancelled": Int64,
    "int_transfers_lodged": Int64,
    "int_transfers_completed": Int64,
    "int_transfers_cancelled": Int64,
    "greenfields_received": Int64,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "dd mmm yyyy",
    "transfers_lodged": "Count of mirn with Created_timestamp = gas_date",
    "transfers_completed": "Count of mirn, change_status = 'COM' with last_updated_timestamp = gas_date",
    "transfers_cancelled": "Count of mirn, change_status = 'CAN' with last_updated_timestamp = gas_date",
    "int_transfers_lodged": "Count of meter_type in ('PC', 'PD') with created_timestamp",
    "int_transfers_completed": "Count of meter_type = 'PC' with last_update",
    "int_transfers_cancelled": "Count of meter_type = 'PD' with last_update",
    "greenfields_received": "Count of mirn with in a mirn_assignment_date",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This public report is to show a general overview of the total retail customer transfers in the market for the previous 12 months.
The report provides some indication of the liquidity in retail churn over the past 12 months and is general information for
management within each respective organisation.

The report consists of a rolling 12-month period and reports transfers that have been lodged, completed or cancelled.
This report provides an indication of market competition and transfer liquidity through the customer transfers.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"

from polars import String, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for LNG Transactions report                   │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "python-configs.bronze_gasbb_lng_transactions"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbblngtransactions*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "TransactionStartDate",
    "TransactionEndDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "TransactionStartDate": String,
    "TransactionEndDate": String,
    "VolWeightPrice": Float64,
    "Volume": Float64,
    "SupplyStartDate": String,
    "SupplyEndDate": String,
}

schema_descriptions = {
    "TransactionStartDate": "Transaction start date.",
    "TransactionEndDate": "Transaction end date.",
    "VolWeightPrice": "The volume weighted price for the reporting period.",
    "Volume": "The total volume of the transactions for the reporting period.",
    "SupplyStartDate": "The earliest start date of all transactions captured in the reporting period.",
    "SupplyEndDate": "The latest end date of all transactions captured in the reporting period.",
}

report_purpose = """
This report displays an LNG transaction aggregated data.

GASBB_LNG_TRANSACTIONS is updated monthly.

Contains all short term LNG Export transactions.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

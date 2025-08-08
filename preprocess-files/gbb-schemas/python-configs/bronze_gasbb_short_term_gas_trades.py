from polars import String, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Short Term Gas Trades report              │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_short_term_gas_trades"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshorttermgastrades*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "PeriodStartDate",
    "PeriodEndDate",
    "State",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "PeriodStartDate": String,
    "PeriodEndDate": String,
    "State": String,
    "Quantity": Float64,
    "VolumeWeightedPrice": Float64,
    "TransactionType": String,
    "SupplyPeriodStart": String,
    "SupplyPeriodEnd": String,
}

schema_descriptions = {
    "PeriodStartDate": "The time period start date.",
    "PeriodEndDate": "The time period end date.",
    "State": "The state where the transaction occurred.",
    "Quantity": "Total volume of the transactions where trade date is in the reporting period for the given state.",
    "VolumeWeightedPrice": "Volume weighted price of transactions where trade date is in the reporting period for the given State.",
    "TransactionType": "Transaction Type is Supply for these short term transactions reports.",
    "SupplyPeriodStart": "The earliest start date of all transactions in the reporting period for the given state.",
    "SupplyPeriodEnd": "The latest end date of all transactions in the reporting period for the given state.",
}

report_purpose = """
These reports display information regarding short term gas transactions.

GASBB_SHORT_TERM_GAS_TRADES_* reports are updated monthly.

Contains all short term gas transactions, excluding those concluded through the gas trading exchange.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

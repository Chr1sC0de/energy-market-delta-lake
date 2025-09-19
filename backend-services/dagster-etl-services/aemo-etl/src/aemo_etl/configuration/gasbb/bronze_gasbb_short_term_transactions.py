from polars import String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_short_term_transactions"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshorttermtransactions*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "PeriodID",
    "State",
    "TransactionType",
    "SupplyPeriodStart",
    "SupplyPeriodEnd",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"


table_schema = {
    "PeriodID": String,
    "State": String,
    "Quantity (TJ)": String,
    "VolumeWeightedPrice ($)": String,
    "TransactionType": String,
    "SupplyPeriodStart": String,
    "SupplyPeriodEnd": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "PeriodID": "Swap period",
    "State": "state for the swap",
    "Quantity (TJ)": "quantity",
    "VolumeWeightedPrice ($)": "volume weighted price",
    "TransactionType": "swap transaction type",
    "SupplyPeriodStart": "supply period start of swap",
    "SupplyPeriodEnd": "supply period endo of swap",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
These reports display short term gas transactions for each state/territory, excluding those transactions that are concluded through an AEMO operated exchange. Reports for VIC and QLD are updated weekly while others are updated monthly.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

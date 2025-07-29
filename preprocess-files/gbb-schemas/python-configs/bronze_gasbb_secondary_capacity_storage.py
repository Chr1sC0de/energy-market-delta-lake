from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Secondary Capacity Storage Trades report  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_secondary_capacity_storage"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshorttermstoragetrading*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "TradeId",
    "VersionDateTime",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "TradeId": Int64,
    "VersionDateTime": String,
    "TradeDate": String,
    "FromGasDate": String,
    "ToGasDate": String,
    "FacilityId": Int64,
    "Priority": String,
    "MaximumStorageQuantity": Int64,
    "InjectionCapacity": Float64,
    "WithdrawalCapacity": Float64,
    "Price": Float64,
    "PriceStructure": String,
    "PriceEscalationMechanism": String,
    "Cancelled": Int64,
    "LastChanged": String,
}

schema_descriptions = {
    "TradeId": "A unique AEMO defined Transaction Identifier.",
    "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",
    "TradeDate": "The date the transaction was entered into.",
    "FromGasDate": "The start date of the transaction.",
    "ToGasDate": "The end date of the transaction.",
    "FacilityId": "The gas storage facility ID for the facility by means of which the service is provided.",
    "Priority": "The priority given to the service to which the transaction relates.",
    "MaximumStorageQuantity": "The storage capacity the subject of the transaction (in GJ).",
    "InjectionCapacity": "The injection capacity (in GJ/day).",
    "WithdrawalCapacity": "The withdrawal capacity (in GJ/day).",
    "Price": "The transaction price (in $/GJ/day or where relevant, in $/GJ).",
    "PriceStructure": "The price structure applicable to the transaction.",
    "PriceEscalationMechanism": "Any price escalation mechanism applicable to the transaction.",
    "Cancelled": "Whether the record has been cancelled.",
    "LastChanged": "The date the record was last updated.",
}

report_purpose = """
This report displays a list of secondary capacity storage trades.

GASBB_SHORT_TERM_STORAGE is generally updated within 30 minutes of receiving new data.

Contains all BB capacity transactions, excluding those concluded through the gas trading exchange.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

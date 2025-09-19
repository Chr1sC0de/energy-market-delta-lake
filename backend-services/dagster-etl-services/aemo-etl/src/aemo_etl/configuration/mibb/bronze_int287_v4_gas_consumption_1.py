from polars import String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int287_v4_gas_consumption_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int287_v4_gas_consumption_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "total_gas_used": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported (e.g. 30 Jun 2007)",
    "total_gas_used": "total gas used in gj",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This public report shows the daily gas consumed  at an operational level and 
therefore will have minor discrepencies due ot metering substitutions or updates
post the gas day
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"

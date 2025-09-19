from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int871_v1_erftdailynslrpt_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int871_v1_erftdailynslrpt_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_id",
    "gas_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "network_id": String,
    "gas_date": String,
    "gas_date_historical": String,
    "nsl_mj": Int64,
    "total_meter_count_basic": Int64,
    "normalisation_factor": Float64,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "network_id": "Network identifier",
    "gas_date": "Gas date being reported",
    "gas_date_historical": "Historical gas date",
    "nsl_mj": "Net section load in MJ",
    "total_meter_count_basic": "Total count of basic meters",
    "normalisation_factor": "Normalisation factor",
    "current_date": "Date and time report produced",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
The ERFTDailyNSLRpt report provides net section load and supporting data for each Network
section, in CSV format from AEMO to Retailers. The report is placed in the MIBB public folder
as a .csv file.

This report is specific to NSW-ACT networks and provides information about the net section load,
total meter count for basic meters, and normalisation factors for each network section.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}"

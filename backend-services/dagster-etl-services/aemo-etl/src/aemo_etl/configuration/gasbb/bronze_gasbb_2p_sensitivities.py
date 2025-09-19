from polars import String, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Reserves And Resources report             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_2p_sensitivities"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbb2psensitivies*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "PeriodID",
    "State",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "PeriodID": String,
    "State": String,
    "Increase": Float64,
    "Decrease": Float64,
    "surrogate_key": String,
}

schema_descriptions = {
    "PeriodID": "relevant periods",
    "State": "state",
    "Increase": "increase value",
    "Decrease": "decrease value",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report displays information about Field Reserves and Resources.

Both GASBB_2P_SENSETIVITIES_ALL and GASBB_2P_SENSETIVITIES_LAST_QUARTER are updated monthly.

Contains all current reserve and resource information for a BB field interest.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

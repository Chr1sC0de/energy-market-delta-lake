from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Basins report                             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_basins"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbbasins*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "BasinId",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {"BasinId": Int64, "BasinName": String, "surrogate_key": String}

schema_descriptions = {
    "BasinId": "A unique AEMO defined Facility Identifier.",
    "BasinName": "The name of the basin. If short name exists then short name included in report.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report displays a list of all basins.

GASBB_BASINS is updated daily.

Contains all current basins.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

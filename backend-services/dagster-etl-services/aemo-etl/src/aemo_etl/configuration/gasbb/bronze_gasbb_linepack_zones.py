from polars import String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Facilities List report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_linepack_zones"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbblinepackzones*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["Operator", "LinepackZone"]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "Operator": String,
    "LinepackZone": String,
    "LinepackZoneDescription": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "Operator": "Operator of linepack zone",
    "LinepackZone": "Linepack Zone",
    "LinepackZoneDescription": "Description of Linepack Zone",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
Display list of operator to linepack zones with descriptions
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

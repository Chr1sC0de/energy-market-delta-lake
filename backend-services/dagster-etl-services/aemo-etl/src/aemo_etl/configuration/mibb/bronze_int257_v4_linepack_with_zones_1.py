from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int257_v4_linepack_with_zones_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int257_v4_linepack_with_zones_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "linepack_zone_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "linepack_zone_id": Int64,
    "linepack_zone_name": String,
    "last_mod_date": String,
    "current_date": String,
}

schema_descriptions = {
    "linepack_zone_id": "Linepack Zone in which the pipe segment exists e.g. 6",
    "linepack_zone_name": "Name of the linepack zone, e.g. Gippsland",
    "last_mod_date": "Time last modified e.g. 20 June 2001 16:39:58",
    "current_date": "Time the report is produced e.g. 21 Jun 2001 16:39:58",
}

report_purpose = """
This report contains the current linepack zones.

This public report is produced when a change occurs.

Each report contains the:
- linepack zone where the pipe segment is located
- linepack zone name
- last modified date and time
- date and time when the report was produced.

Note: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

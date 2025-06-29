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


table_name = "bronze_int258_v4_mce_nodes_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int258_v4_mce_nodes_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "pipeline_id",
    "point_group_identifier_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "pipeline_id": Int64,
    "point_group_identifier_id": Int64,
    "point_group_identifier_name": String,
    "nodal_altitude": Int64,
    "last_mod_date": String,
    "current_date": String,
}

schema_descriptions = {
    "pipeline_id": "Pipeline identifier e.g. 1",
    "point_group_identifier_id": "Point group identifier e.g. 4",
    "point_group_identifier_name": "Point group identifier name e.g. Rosebud",
    "nodal_altitude": "Nodal altitude e.g. 37",
    "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:42:35",
    "current_date": "Date and Time the report is produced e.g. 21 Jun 2001 16:42:35",
}

report_purpose = """
This report contains the current MCE Nodes.

This public report is produced each time a change occurs.
It identifies nodes that the MCE uses. The nodal prices from MCE forms the network prices.

Each report contains the:
- pipeline identifier
- point group identifier and name
- nodal altitude
- last modified date
- date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

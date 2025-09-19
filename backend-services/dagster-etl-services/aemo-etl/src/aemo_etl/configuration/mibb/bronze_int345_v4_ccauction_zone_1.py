from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int345_v4_ccauction_zone_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int345_v4_ccauction_zone_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "zone_id",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "zone_id": Int64,
    "zone_name": String,
    "zone_type": String,
    "from_date": String,
    "to_date": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "zone_type": "Type of CC zone. Entry/Exit",
    "from_date": "Effective from date of the zone",
    "to_date": "Effective end date of the zone",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report provides a listing of the CC zones.

This report will be regenerated when CC zone data is updated.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

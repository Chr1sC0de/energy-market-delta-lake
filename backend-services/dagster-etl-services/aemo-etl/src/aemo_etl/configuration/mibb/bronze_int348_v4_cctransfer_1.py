from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int348_v4_cctransfer_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int348_v4_cctransfer_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "transfer_id",
    "zone_id",
    "start_date",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "transfer_id": Int64,
    "zone_id": Int64,
    "zone_name": String,
    "start_date": String,
    "end_date": String,
    "transferred_qty_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "transfer_id": "Identifier number of the CC transfer",
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "start_date": "Starting CC product period start date. Dd mmm yyyy",
    "end_date": "Ending CC product period end date. Dd mmm yyyy",
    "transferred_qty_gj": "CC amount in GJ transferred in the denoted transfer id",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the approved CC transfer amounts conducted on the previous day.

This report will be published on the following gas day (D+1) if a transfer of capacity certificates has been approved on the
previous gas day. The report will be published at midnight. If no transfer of capacity certificates has been approved, the report
will not be published.
The report provides information about the amount of CC transferred for a CC zone and CC product period.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

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

table_name = "bronze_int351_v4_ccregistry_summary_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int351_v4_ccregistry_summary_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "zone_id",
    "start_date",
    "end_date",
    "source",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "zone_id": Int64,
    "zone_name": String,
    "zone_type": String,
    "start_date": String,
    "end_date": String,
    "total_holding_gj": Float64,
    "source": String,
    "current_date": String,
}

schema_descriptions = {
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "zone_type": "Type of CC zone. Entry/Exit",
    "start_date": "Starting CC product period start date. Dd mmm yyyy",
    "end_date": "Ending CC product period end date. Dd mmm yyyy",
    "total_holding_gj": "Total holding in GJ",
    "source": "Acquired source of the holding. Eg: AUCTION, DTSSP14",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides a registry of the capacity certificates allocated to each auction product.

This report will provide the total capacity certificates that is allocated at each CC zone and period. The report aggregates the
CC quantities won and paid for by all Market participants in a CC Auction for a CC zone and period. The report also provides
quantities allocated by the DTS SP.
This report is published daily at midnight.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

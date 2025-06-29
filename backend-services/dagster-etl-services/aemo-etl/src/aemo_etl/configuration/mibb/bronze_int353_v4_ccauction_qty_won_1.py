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

table_name = "bronze_int353_v4_ccauction_qty_won_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int353_v4_ccauction_qty_won_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "zone_id",
    "cc_period",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)


table_schema = {
    "auction_id": Int64,
    "auction_date": String,
    "zone_id": Int64,
    "zone_name": String,
    "zone_type": String,
    "start_date": String,
    "end_date": String,
    "cc_period": String,
    "clearing_price": Float64,
    "quantities_won_gj": Float64,
    "unallocated_qty": Float64,
    "current_date": String,
}

schema_descriptions = {
    "auction_id": "Identifier number of the CC auction",
    "auction_date": "Auction run date. dd mmm yyyy",
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "zone_type": "Type of CC zone. Entry/Exit",
    "start_date": "Starting CC product period start date. Dd mmm yyyy",
    "end_date": "Ending CC product period end date. Dd mmm yyyy",
    "cc_period": "CC product period name representing date range period for the capacity",
    "clearing_price": "Price in which bid cleared",
    "quantities_won_gj": "Quantity won in GJ",
    "unallocated_qty": "Quantity not won in GJ",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the CC capacities won at auction for the published CC auction by zone and period.

A report is produced on approval of the CC auction results for a CC auction <ID>.
This report will show the CC auction results in csv format.
Aggregation of all quantities won by all Market participants.
Sort order is by Zone ID, calendar months for the years within auction period range.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

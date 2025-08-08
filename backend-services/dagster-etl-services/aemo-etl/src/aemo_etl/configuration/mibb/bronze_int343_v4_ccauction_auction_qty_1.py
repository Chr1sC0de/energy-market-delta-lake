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

table_name = "bronze_int343_v4_ccauction_auction_qty_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int343_v4_ccauction_auction_qty_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "zone_id",
    "capacity_period",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "auction_id": Int64,
    "zone_id": Int64,
    "zone_name": String,
    "zone_type": String,
    "capacity_period": String,
    "auction_date": String,
    "available_capacity_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "auction_id": "Identifier number of the CC auction",
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "zone_type": "Type of CC zone. Entry/Exit",
    "capacity_period": "Date ranged period the CC product applies to",
    "auction_date": "Auction run date. dd mmm yyyy",
    "available_capacity_gj": "Available capacity to bid on for opened auction in GJ",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the CC capacities available for auction by zone and period after the announcement that the CC auction is
open.

A report is produced when CC auction is triggered.
This report will show the auctionable quantity for each product for a particular auction ID in csv format.
Sort order is by Zone and Capacity Period in ascending order.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

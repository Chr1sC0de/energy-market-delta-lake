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

table_name = "bronze_int339_v4_ccauction_bid_stack_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int339_v4_ccauction_bid_stack_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "bid_id",
    "zone_id",
    "step",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "auction_id": Int64,
    "auction_date": String,
    "bid_id": Int64,
    "zone_id": Int64,
    "zone_name": String,
    "start_period": String,
    "end_period": String,
    "step": Int64,
    "bid_price": Float64,
    "bid_quantity_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "auction_id": "Identifier number of the CC auction",
    "auction_date": "Auction run date. dd mmm yyyy",
    "bid_id": "Bid identifier",
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "start_period": "Starting CC product period representing date range period for the capacity",
    "end_period": "Ending CC product period representing date range period for the capacity",
    "step": "Bid step number",
    "bid_price": "CC auction bid step price",
    "bid_quantity_gj": "CC auction bid step quantity",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the entire bid stack information without participant data identifying data for the current (latest) CC auction
as denoted by the auction ID number.

This report provides the final capacity certificate bid stack data for the current (latest) auction published.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

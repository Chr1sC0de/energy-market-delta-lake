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


table_name = "bronze_int112b_v4_nftc_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int112b_v4_nftc_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["nftc_name", "commencement_date", "ti"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "nftc_name": String,
    "commencement_date": String,
    "termination_date": String,
    "daily_max_net_inj_qty_gj": Int64,
    "daily_max_net_wdl_qty_gj": Int64,
    "ti": Int64,
    "hourly_max_net_inj_qty_gj": Int64,
    "hourly_max_net_wdl_qty_gj": Int64,
    "mod_datetime": String,
    "current_date": String,
}

schema_descriptions = {
    "nftc_name": "Name of the Net Flow Transportation Constraint",
    "commencement_date": "e.g. 27 Jun 2011. Dates that mark the boundary of the application of the constraint",
    "termination_date": "e.g. 27 Jun 2011. Dates that mark the boundary of the application of the constraint",
    "daily_max_net_inj_qty_gj": "The aggregate maximum daily injection limit in gigajoules applied by this constraint",
    "daily_max_net_wdl_qty_gj": "The aggregate maximum daily withdrawal limit in gigajoules applied by this constraint",
    "ti": "Time interval 1-24 (hour of the gas day)",
    "hourly_max_net_inj_qty_gj": "1 value for each hour of the gas day",
    "hourly_max_net_wdl_qty_gj": "1 value for each hour of the gas day",
    "mod_datetime": "NFTC creation/modification time stamp e.g. 07 Jun 2011 08:01:23",
    "current_date": "Date and time the report was produced",
}

report_purpose = """
This report contains information on group directional flow point constraints (DFPCs) pertaining to the DTS. Grouped directional flow
points are those points in the DTS where multiple injections and withdrawals can occur.

This report contains flow constraints for a group of meters typically at the same location.

NFTCs are part of the configuration of the network that can be manually changed by the AEMO Schedulers, and form one of the inputs
to the schedule generation process.

Traders can use this information to understand the network-based restrictions that will constrain their ability to offer gas to the market on
a given day in the reporting window.

(See Also INT112)
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int112b_v5_nftc_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int112b_v5_nftc_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "nftc_name",
    "commencement_date",
    "ti",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "nftc_name": String,
    "commencement_date": String,
    "termination_date": String,
    "daily_max_net_inj_qty_gj": Int64,
    "daily_min_net_inj_qty_gj": Int64,
    "daily_max_net_wdl_qty_gj": Int64,
    "daily_min_net_wdl_qty_gj": Int64,
    "ti": Int64,
    "hourly_max_net_inj_qty_gj": Int64,
    "hourly_min_net_inj_qty_gj": Int64,
    "hourly_max_net_wdl_qty_gj": Int64,
    "hourly_min_net_wdl_qty_gj": Int64,
    "mod_datetime": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "nftc_name": "Name of the Net Flow Transportation Constraint",
    "commencement_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2011)",
    "termination_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2011)",
    "daily_max_net_inj_qty_gj": "The aggregate maximum daily injection limit in gigajoules applied by this constraint",
    "daily_min_net_inj_qty_gj": "The aggregate minimum daily injection limit in gigajoules applied by this constraint",
    "daily_max_net_wdl_qty_gj": "The aggregate maximum daily withdrawal limit in gigajoules applied by this constraint",
    "daily_min_net_wdl_qty_gj": "The aggregate minimum daily withdrawal limit in gigajoules applied by this constraint",
    "ti": "Time interval 1-24 (hour of the gas day)",
    "hourly_max_net_inj_qty_gj": "1 value for each hour of the gas day",
    "hourly_min_net_inj_qty_gj": "1 value for each hour of the gas day",
    "hourly_max_net_wdl_qty_gj": "1 value for each hour of the gas day",
    "hourly_min_net_wdl_qty_gj": "1 value for each hour of the gas day",
    "mod_datetime": "NFTC creation/modification time stamp (e.g. 07 Jun 2011 08:01:23)",
    "current_date": "Date and time the report was produced (e.g. 30 Jun 2011 1:23:56)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report contains information on group directional flow point constraints (DFPCs) pertaining to the DTS. Grouped
directional flow points are those points in the DTS where multiple injections and withdrawals can occur.

This report contains flow constraints for a group of meters typically at the same location.
NFTCs are part of the configuration of the network that can be manually changed by the AEMO Schedulers, and form one of
the inputs to the schedule generation process.

Traders can use this information to understand the network-based restrictions that will constrain their ability to offer gas to the
market on a given day in the reporting window.

A report is produced each time an operational schedule (OS) is approved by AEMO. Therefore, it is expected that each day
there will be at least 9 of these reports issued:
- 5 being for the standard current gas day schedules
- 3 being for the standard 1 ahead schedules
- 1 being for the standard 2 days ahead schedule.

Each report contains details of the NFTCs that have applied and will apply to schedules run:
- on the previous gas day
- for the current gas day
- for the next 2 gas days.

Each NFTC has a unique identifier and applies to a single group of MIRNs (an injection MIRN and a withdrawal MIRN).
Each row in the report contains details of one NFTC for one hour of the gas day, with hourly intervals commencing from the
start of the gas day. That is, the first row for a NFTC relates to 06:00 AM.

This report will contain 24 rows for each NFTC for each gas day reported.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int583_v4_monthly_cumulative_imb_pos_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int583_v4_monthly_cumulative_imb_pos_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
    "fro_name",
    "distributor_name",
    "withdrawal_zone",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "network_name": String,
    "version_id": Int64,
    "fro_name": String,
    "distributor_name": String,
    "withdrawal_zone": String,
    "curr_cum_date": String,
    "curr_cum_imb_position": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "network_name": "Network Name",
    "version_id": "Settlement statement version identifier",
    "fro_name": "Name of Financially Responsible Organisation",
    "distributor_name": "Distribution business name",
    "withdrawal_zone": "Withdrawal zone",
    "curr_cum_date": "Current cumulative imbalance issue date",
    "curr_cum_imb_position": "Surplus or Deficit or Balance",
    "current_date": "Date and Time report produced 15 Aug 2007 10:06:54",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report shows the cumulative imbalance position of Retailers. Retailers may wish to use this report to track their status of
the imbalance to do the necessary adjustments.

This public report is updated at each issue of settlement to show the status of each retailer's imbalance position.
There is no equivalent VIC MIBB report.

Each report contains the:
- network name
- statement version id
- financially Responsible Organisation
- distributor Name
- withdrawal zone
- current cumulative imbalance issue date
- current cumulative imbalance position (Surplus, Deficit or Balanced)
- date and time report produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}"

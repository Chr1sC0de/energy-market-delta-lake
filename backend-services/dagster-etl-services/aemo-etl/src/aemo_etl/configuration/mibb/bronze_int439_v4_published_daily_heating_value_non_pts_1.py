from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int439_v4_published_daily_heating_value_non_pts_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int439_v4_published_daily_heating_value_non_pts_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "gas_day",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "network_name": String,
    "gas_day": String,
    "heating_value": Float64,
    "current_date": String,
}

schema_descriptions = {
    "network_name": "Network name",
    "gas_day": "Gas day being reported e.g. 30 Jun 2007",
    "heating_value": "Heating Value",
    "current_date": "Time Report Produced e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This report provides the publish heating values.

This public report is produced daily.
Only reports the non-DTS (Declared transmission) networks.

Note: This report is decommissioned from December 2024.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"

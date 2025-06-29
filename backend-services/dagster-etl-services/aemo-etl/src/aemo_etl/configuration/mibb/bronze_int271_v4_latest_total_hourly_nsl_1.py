from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int271_v4_latest_total_hourly_nsl_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int271_v4_latest_total_hourly_nsl_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_id",
    "gas_date",
    "ti",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "network_id": String,
    "nsl_update": String,
    "gas_date": String,
    "ti": Int64,
    "nsl_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "network_id": "Network ID of NSL",
    "nsl_update": "Time profile created",
    "gas_date": "Primary key for MIBB report (e.g. 30 Jun 2007)",
    "ti": "Time Interval (1-24)",
    "nsl_gj": "Hourly nsl total for all DB",
    "current_date": "Date and Time report created (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This public report is to provide a 3-year rolling history for network system load (NSL) on an hourly basis for both DTS and non-DTS Networks. 
This report may be used to review non-daily metered load profiles across each network and to forecast non-daily metered load shape in each distribution network area.

Participants may wish to use this data as an input into their forecasting systems to assist in predicting the daily profile of their
non-daily read customers' meters. It should be noted that the larger the number of non-daily read meters for which a Market
participant is the FRO, the NSL will better approximate the hourly behaviour of the Market participants non-daily read load.

Section 2.8.4 of the Victorian Retail Market Procedures AEMO's obligation to publish the NSL and Attachment 6 of the
Victorian Retail Market Procedures set out how AEMO calculates the NSL.

A report contains data which is grouped by network identifier which is used to distinguish non-DTS networks from the DTS
network.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"

from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int037c_v4_indicative_price_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int037c_v4_indicative_price_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["demand_type_name", "transmission_id"]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "demand_type_name": String,
    "price_value_gst_ex": Float64,
    "transmission_group_id": Int64,
    "schedule_type_id": String,
    "transmission_id": Int64,
    "gas_date": String,
    "approval_datetime": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "demand_type_name": "Normal Uses Demand forecast used by operational schedule",
    "price_value_gst_ex": "Forecast market price ($) for BoD Scheduling horizon of the gas day in question",
    "transmission_group_id": "Link to the related day(s) ahead operational schedule",
    "schedule_type_id": "OS (Operating Schedule Id)",
    "transmission_id": "Schedule number these prices are related to",
    "gas_date": "e.g. 30 Jun 2007",
    "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",
    "current_date": "Date and time the report is produced e.g. 29 Jun 2007 01:23:45",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to indicate what the prices are for the day and what they are predicted to be for the next two days.

Market participants may wish to use this information to estimate pricing for the following two days.

This report is produced after the approval of each schedule. The report has the actual price information of each operating
schedule, as well as forecast process for the day ahead schedules published. This means that on any given gas day the report
is published:
- 5 times for Day+0 after each of the 5 market schedules which reflects actual price that applies for each scheduling horizon.
- 3 times for Day+1 which includes the estimated BoD price.
- Once for Day+2 which includes the estimated BoD price.

Participants can use this report to review the outcomes of the current day and to reflect on the options to adjust their positions
for the coming days.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

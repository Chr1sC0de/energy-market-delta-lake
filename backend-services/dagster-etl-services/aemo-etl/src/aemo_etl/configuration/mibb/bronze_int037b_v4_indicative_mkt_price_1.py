from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int037b_v4_indicative_mkt_price_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int037b_v4_indicative_mkt_price_1*"

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
    "demand_type_name": """Normal Uses Demand forecast used by operational schedule
10% exceedence means the estimated market price is based on
10 % exceedance of the forecast demand level.
90% exceedence means the estimated market price if the demand
is 90 % of the the forecast demand.""",
    "price_value_gst_ex": "Forecast market price ($) for BoD Scheduling horizon of the gas day in question",
    "transmission_group_id": "Link to the related day(s) ahead operational schedule",
    "schedule_type_id": "MS (Market Schedule Id)",
    "transmission_id": "Schedule number these prices are related to",
    "gas_date": "e.g. 30 Jun 2007",
    "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",
    "current_date": "Date and time Report Produced e.g. 29 Jun 2007 01:23:45",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to indicate what the prices are for the day and what they are predicted to be for the next two days.

Market participants may wish to use this information to estimate pricing for the following two days.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

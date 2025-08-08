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


table_name = "bronze_int153_v4_demand_forecast_rpt_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int153_v4_demand_forecast_rpt_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "forecast_date",
    "version_id",
    "ti",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "forecast_date": String,
    "version_id": Int64,
    "ti": Int64,
    "forecast_demand_gj": Int64,
    "vc_override_gj": Int64,
    "current_date": String,
}

schema_descriptions = {
    "forecast_date": "Gas date of forecast e.g. 30 Jun 2007",
    "version_id": "Forecast version used to identify which forecast was used in the schedule (reference INT108)",
    "ti": "Time interval (1-24)",
    "forecast_demand_gj": "Forecast total hourly demand (in GJ/hour) potentially used as input in the MCE",
    "vc_override_gj": "Quantity (in GJ) of any AEMO override (can be either positive or negative)",
    "current_date": "Date and time report produced",
}

report_purpose = """
This report is created each time AEMO generates and saves a demand forecast. Note this may occur many times prior to the
running of a schedule as AEMO tests the feasibility of the different variables used in a schedule. The report provides:
- the total uncontrollable withdrawal quantity that may be used as input in the production of a schedule
- the quantity (positive or negative) by which AEMO deems it necessary to adjust Market participant submissions in
  order to maintain system security.

Participants may use this report to gauge AEMO's schedulers view of the current day situation and whether the aggregate of
all Participants demand forecasts sum to an adequate demand value and/or profile given AEMO's perspective of the system
demands of the gas day.

As not every saved forecast demand generated is used in the scheduling process, Market participants need to reference
INT108 Schedule Run Log to determine which Demand Forecast was actually used in scheduling.

The INT108 forecast_demand_version will specify which INT053 rows will provide information that was used by AEMO in its
scheduling processes.

This report is generated each time AEMO generates and saves a demand forecast. Each report provides details of all the
demand forecasts created up to the report generation time on the current gas day.

A given report may contain demand forecasts that are for:
- the current day
- 1 day ahead
- 2 days ahead
- 3 days ahead

By comparing the forecast_date with the current_date, users will be able to determine the type of forecast for a particular
forecast (version_id) (i.e. whether it is for the current day or a day ahead schedule)

Each row in a report provides the forecast demand and the AEMO override (in GJ) for the specified hour of the gas day of the
specified demand forecast. Therefore, there will be 24 rows in the report for each demand forecast.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

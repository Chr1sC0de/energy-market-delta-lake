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


table_name = "bronze_int108_v4_scheduled_run_log_7_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int108_v4_scheduled_run_log_7_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["transmission_document_id"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "transmission_id": Int64,
    "transmission_document_id": Int64,
    "transmission_group_id": Int64,
    "gas_start_datetime": String,
    "bid_cutoff_datetime": String,
    "schedule_type_id": String,
    "creation_datetime": String,
    "forecast_demand_version": String,
    "dfs_interface_audit_id": Int64,
    "last_os_for_gas_day_tdoc_id": Int64,
    "os_prior_gas_day_tdoc_id": Int64,
    "approval_datetime": String,
    "demand_type_id": Int64,
    "objective_function_value": Float64,
    "current_date": String,
}

schema_descriptions = {
    "transmission_id": "Transmission ID",
    "transmission_document_id": "Unique identity for each schedule",
    "transmission_group_id": "To link the Operational Schedule to the Market Schedule of an ante schedule",
    "gas_start_datetime": "Similar to Schedule_Start_date but not absolute (Trading between midnight and 6:00 AM is considered to be belonged to the previous day)",
    "bid_cutoff_datetime": "If the submission datetime is after the datetime specified by this Bid_Cutoff_Date then the nomination (or bids) is used",
    "schedule_type_id": "'MS' Market Schedule, 'OS' Operational Schedule",
    "creation_datetime": "When schedule is created",
    "forecast_demand_version": "Version as listed in the TMM database",
    "dfs_interface_audit_id": "Version as stored in the DFS database",
    "last_os_for_gas_day_tdoc_id": "Last Operating schedule for the day either a 1 PM or an ad hoc",
    "os_prior_gas_day_tdoc_id": "Last Operating schedule for the previous day either a 1 PM or an ad hoc",
    "approval_datetime": "Date and time of approval",
    "demand_type_id": "Type of demand: '0' = Normal, '1' = Plus 10 percent, '2' = Minus 10 percent",
    "objective_function_value": "Objective_Function_Value for each run. This value is returned from the MCE",
    "current_date": "Date and Time Report Produced",
}

report_purpose = """
This report lists all the schedules that have been run for the previous 7 gas days. It provides transparency of AEMO demand
forecasting and scheduling activities on the basis of inputs from Market participants and weather forecasts.

For instance, Participants may wish to rely on the information provided in this report for reconciliation of the scheduling
process delivered by AEMO. The quantities and prices for each of the standard schedules in the reporting window are
identified by the unique schedule identifiers (transmission_id and transmission_document_id) to assist with tracking the
process across the day.

This report contains details for each of the schedules run for the previous 7 gas days. It includes both:
- standard schedules (such as the schedules published at fixed times specified in the NGR); and
- any ad hoc schedules

Information in the report can be linked to Participants demand forecasting activities. For example, see "INT126 - DFS Data"
and "INT153 - Demand Forecast" for quantities and prices.

Each report identifies each of the schedules run for the previous 7 gas days. For each day in the reporting window, 
there will be at least 18 rows of data:
- 5 being for the standard current gas day operational schedules
- 5 being for the standard current gas day pricing schedules
- 3 being for the standard 1-day ahead operational schedules
- 3 being for the standard 1-day ahead pricing schedules
- 1 being for the standard 2 days ahead operational schedule
- 1 being for the standard 2 days ahead pricing schedule

Each schedule run in the previous 7 gas days is identified in a separate row of the report.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int310_v4_price_and_withdrawals_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int310_v4_price_and_withdrawals_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "schedule_interval",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "schedule_interval": Int64,
    "transmission_id": Int64,
    "sched_inj_gj": Float64,
    "sched_wdl_gj": Float64,
    "price_value": Float64,
    "administered_price": Float64,
    "actual_wdl_gj": Float64,
    "actual_inj_gj": Float64,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "dd mmm yyyy",
    "schedule_interval": "(1,2,3,4 or 5)",
    "transmission_id": "Schedule ID",
    "sched_inj_gj": "Last approved scheduled injections",
    "sched_wdl_gj": "Last approved scheduled withdrawals including controllable withdrawals",
    "price_value": "Price value",
    "administered_price": "Administered Price",
    "actual_wdl_gj": "Actual metered withdrawals",
    "actual_inj_gj": "Actual metered injections",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to show the overall statistics for gas days for the last 12 months. Participants may wish to use this report as a
market analysis tool for forecasting purposes, and general information for management within their respective organisations.

A report is produced daily covering the previous rolling 12-month period.
The report provides information about scheduled gas injections and withdrawals and actual system performance for the
previous 12 months.

Each report contains the:
- gas date
- schedule interval (indicating 1 to 5 when the deviation occurred, where 1 refers to 6:00 AM to 10:00 AM, 2 will relate to
10:00 AM to 2:00 PM, and so forth)
- transmission identifier for the schedule
- scheduled injections in gigajoules
- scheduled withdrawals in gigajoules
- price for the scheduling horizons
- Administered Price (the value in the admin price field is null when no admin prices applies and when there has been an
admin price, it will be displayed and the price_value will show the last approved schedule price)
- Actual metered withdrawals in gigajoules
- Actual metered injections in gigajoules
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

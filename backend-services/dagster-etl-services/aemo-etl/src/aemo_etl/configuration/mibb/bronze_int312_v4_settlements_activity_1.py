from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int312_v4_settlements_activity_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int312_v4_settlements_activity_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "uafg_28_days_pct": Float64,
    "total_scheduled_inj_gj": Float64,
    "total_scheduled_wdl_gj": Float64,
    "total_actual_inj_gj": Float64,
    "total_actual_wdl_gj": Float64,
    "total_uplift_amt": Float64,
    "su_uplift_amt": Float64,
    "cu_uplift_amt": Float64,
    "vu_uplift_amt": Float64,
    "tu_uplift_amt": Float64,
    "ru_uplift_amt": Float64,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "dd mmm yyyy",
    "uafg_28_days_pct": "Uafg-28-day-rolling in pct",
    "total_scheduled_inj_gj": "Total scheduled injection in GJ",
    "total_scheduled_wdl_gj": "Sum of total scheduled controllable withdrawals, demand forecasts and AEMO's over-ride in GJ",
    "total_actual_inj_gj": "Total actual injection in GJ",
    "total_actual_wdl_gj": "Total actual withdrawals in GJ",
    "total_uplift_amt": "Total uplift in $",
    "su_uplift_amt": "Total surprise uplift in $",
    "cu_uplift_amt": "Total congestion uplift in $",
    "vu_uplift_amt": "Total common uplift resulting from unallocated AEMO's demand forecast over-ride in $",
    "tu_uplift_amt": "Total common uplift from exceedance of DTSP's liability limit in $",
    "ru_uplift_amt": "Total residual commin uplift in $",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to provide the market with information about settlement activity for the previous 12 months. Participants may
wish to use this report to monitor market activity in the industry.

A report is produced daily to the public with a rolling 12-month period.
"uafg" in the second column of the report refers to unaccounted for gas shown in percentage. This could be due to a number of
reasons, such as measurement errors or leakages. This report will show the "uatg" for a rolling 28-day period.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"

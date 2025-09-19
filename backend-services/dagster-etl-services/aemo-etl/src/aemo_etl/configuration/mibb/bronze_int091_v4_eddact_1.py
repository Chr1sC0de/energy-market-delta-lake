from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int091_v4_eddact_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int091_v4_eddact_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["edd_update", "edd_date"]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "edd_update": String,
    "edd_date": String,
    "edd_value": Float64,
    "edd_type": Int64,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "edd_update": "Date and time value derived e.g. 27 Sep 2007 14:31:00",
    "edd_date": "Actual EDD date (event date) (e.g. 30 Jun 2007)",
    "edd_value": "EDD value",
    "edd_type": "=1 Billing EDD, used in BMP for generating consumed energy values and remains based on the 9-9 time period, even though the gas day is 6-6",
    "current_date": "Time Report Produced (e.g. 30 Jun 2007 06:00:00) Time Report Produced e.g. 29 Jun 2007 01:23:45",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report provides the Effective Degree Day (EDD) as calculated for a gas day in AEMO's settlements processing. This
settlements EDD value is used in the generation of energy values used by AEMO to settle the wholesale market.

Gas distributors and retailers use the information in this report to derive an average EDD figure for use in their own routines to
estimate end-use customers' consumption where no actual read is available for a basic meter. The Victorian Retail Market
Procedures prescribes AEMO requirement to publish the EDD (see section 2.8.2), how AEMO calculates the EDD (see
attachment 6 section 3) and the use of this EDD value when generating an estimated meter reading (see attachment 4).

The reported EDD is an actual EDD (i.e. Based on actual weather observations rather than weather forecasts) and is
calculated for a 9-9 time period rather than a 6-6 gas day. It should also be noted that the published EDD value is not normally
subject to revision.

This report is generated daily. Each report provides a historical record of actual EDD for a rolling 2 calendar month period
ending on the day before the report date.

Each row in the report provides the billing EDD for the specified edd_date.

Since actual EDD is calculated on actual weather observations, the latest possible EDD available is for the previous full day.
This means that actual EDD is always published (at least) 1 day in arrears.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"

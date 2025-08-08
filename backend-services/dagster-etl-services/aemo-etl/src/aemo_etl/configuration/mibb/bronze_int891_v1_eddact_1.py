from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int891_v1_eddact_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int891_v1_eddact_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["edd_update", "edd_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "edd_update": String,
    "edd_date": String,
    "edd_value": Float64,
    "edd_type": Int64,
    "current_date": String,
}

schema_descriptions = {
    "edd_update": "Date and time value derived e.g. 27 Sep 2007 14:33:00",
    "edd_date": "Actual EDD date (event date) (e.g. 30 Jun 2007)",
    "edd_value": "EDD value",
    "edd_type": "=3 for NSW/ACT EDD",
    "current_date": "Time Report Produced (e.g. 30 Apr 2015 18:00:03)",
}

report_purpose = """
This report provides the separate Effective Degree Day (EDD) values for NSW and ACT as
calculated for a gas day.

Gas distributors and retailers use the information in this report to derive an average EDD
figure for use in their own routines to estimate end-use customers' consumption where no
actual read is available for a basic meter. The NSW/ACT Retail Market Procedures prescribes
AEMO requirement to publish the EDD, how AEMO calculates the EDD (refer Attachment 2)
and the use of this EDD value when generating an estimated meter reading (see Attachment 2
and 3).

The reported EDD is an actual EDD (i.e. Based on actual weather observations rather than
weather forecasts) and is calculated for a time period as specified under Attachment 2 of the
NSW/ACT RMP. It should also be noted that the published EDD value is not normally subject
to revision.

This report is generated daily. Each report provides a historical record of actual EDD for a
rolling 60 day period ending on the day before the report date.

Each row in the report provides the EDD for the specified edd_date.

Since actual EDD is calculated on actual weather observations, the latest possible EDD
available is for the previous full day. This means that actual EDD is always published (at least)
1 day in arrears.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}"

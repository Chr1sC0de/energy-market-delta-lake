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


table_name = "bronze_int171_v4_latest_nsl_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int171_v4_latest_nsl_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "nsl_update",
    "gas_date",
    "distributor_name",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "nsl_update": String,
    "gas_date": String,
    "distributor_name": String,
    "nsl_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "nsl_update": "Time profile created",
    "gas_date": "Primary key for MIBB report (e.g. 30 Jun 2007)",
    "distributor_name": "Primary Key for MIBB report",
    "nsl_gj": "Daily nsl energy for a DB",
    "current_date": "Time report created (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report is to list the Net System Load (NSL) for each distribution area for a rolling 3 year period. This report may be used to
validate consumed energy produced in INT169. Section 2.8.4 of the Victorian Retail Market Procedures AEMO's obligation to
publish the NSL and Attachment 6 of the Victorian Retail Market Procedures set out how AEMO calculates the NSL.

This public report is updated daily and reflects data which is one business day after the gas date (Day + 1).
This report only applies to the DTS network.

The NSL is defined as the total injection into a distribution business network minus the daily metered load (i.e. all the interval
metered sites). It therefore represents the consumption profile of all the non-daily read meters (basic meters).
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"

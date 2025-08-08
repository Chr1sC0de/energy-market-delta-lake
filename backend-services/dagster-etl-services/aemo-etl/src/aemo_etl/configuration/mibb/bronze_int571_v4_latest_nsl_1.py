from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int571_v4_latest_nsl_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int571_v4_latest_nsl_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "gas_date",
    "distributor_name",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "nsl_update": String,
    "network_name": String,
    "gas_date": String,
    "distributor_name": String,
    "nsl_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "nsl_update": "Date and Time profile created",
    "network_name": "Network name",
    "gas_date": "Gas date being reported",
    "distributor_name": "Distribution region",
    "nsl_gj": "Daily nsl energy for a DB",
    "current_date": "Date and Time report created (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report is to list the Net System Load (NSL) for each distribution area for a rolling 3 year period. This report may be used to
validate consumed energy produced in INT569.

Attachment 4 of the Queensland Retail Market Procedures describes the NSL in further detail.

This public report is updated daily and reflects data which is one business day after the gas date (Day + 1).
The NSL is defined as the total injection into a distribution business network minus the daily metered load (ie all the interval
metered sites). It therefore represents the total consumption profile of all the non-daily read meters (basic meters).

This report is similar to VIC MIBB report INT471.

Each report contains the:
- date and time when the NSL profile was updated
- network name
- gas date
- distributor name
- daily NSL energy in gigajoules for a distribution business
- date and time the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}"

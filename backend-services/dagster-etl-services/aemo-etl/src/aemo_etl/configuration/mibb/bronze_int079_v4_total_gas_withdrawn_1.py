from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int079_v4_total_gas_withdrawn_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int079_v4_total_gas_withdrawn_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "unit_id": String,
    "qty": Float64,
    "qty_reinj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported e.g. 30 Jun 2007",
    "unit_id": "Unit of measurement (GJ)",
    "qty": "Total Gas withdrawn Daily",
    "qty_reinj": "Total Net Gas withdrawn Daily (Withdrawals less re-injections)",
    "current_date": "Date and time report produced e.g. 30 Jun 2007 01:23:45",
}

report_purpose = """
This report provides a view of the total quantity of gas that is flowing in the DTS on a given day. Retailers may use this
information as an input to their demand forecasts or to estimate their market share. Participants must be aware that the data is
of operational quality and not settlement quality, and is therefore subject to revision. The data revisions can be significant and
is dependent on a number of factors, including, but not limited to, the availability of telemetered data and system availability.

The report contains metering data for the prior gas day. The data is of operational quality and is subject to substitution and
replacement.

In the context of this report, re-injections represent the flow to the transmission pipeline system (TPS) from the distribution
pipeline system (DPS) at times of low pressure and low demand. The first quantity reported, "qty", includes re-injections.

It should be noted that for a single day, multiple entries can exist. Initial uploads of data for a given date can be incomplete
when it is first reported and updates arriving later into AEMO's system will cause multiple entries to exist, Participants should
combine the reports to provide a daily total.

Each report contains details of the withdrawals that occurred on the previous seven gas days. That is, the INT079 report for
the gas date of 11-August will contain withdrawal quantities for the dates 4 to 10 August inclusive.

The data in this report can have a significant number of substituted values and it is possible for the data to change from day to
day as they are updated through the 7-day reporting window.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"

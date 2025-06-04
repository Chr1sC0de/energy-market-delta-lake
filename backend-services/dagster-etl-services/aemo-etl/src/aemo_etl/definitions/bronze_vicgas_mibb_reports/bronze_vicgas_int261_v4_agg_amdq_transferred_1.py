from polars import Date, Datetime, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import (
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int261_v4_agg_amdq_transferred_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int261_v4_agg_amdq_transferred_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": Date,
    "aggregated_amdq_transferred": Float64,
    "current_date": Datetime(time_unit="ms", time_zone="UTC"),
}

schema_descriptions = {
    "gas_date": "Gas day being reported e.g. 02 Feb 2001",
    "aggregated_amdq_transferred": "Total AMDQ transffered each day for the previous month",
    "current_date": "Date and Time report produced e.g. 30 Jun 2007 06:00:00",
}

report_purpose = """
This report displays the aggregated AMDQ transfer quantities for the previous 30 days. It registers the daily off market trades and
transfer amounts.

A market participant report is produced on a monthly basis showing the total AMDQ transferred each day for the previous 30 days.

Each report contains:
- the gas date
- the aggregated AMDQ transferred
- the date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


definition_builder = definition_builder_factory(
    report_purpose,
    table_schema,
    schema_descriptions,
    primary_keys,
    upsert_predicate,
    s3_table_location,
    s3_prefix,
    s3_file_glob,
    table_name,
    group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
)

definitions_list.append(definition_builder.build())

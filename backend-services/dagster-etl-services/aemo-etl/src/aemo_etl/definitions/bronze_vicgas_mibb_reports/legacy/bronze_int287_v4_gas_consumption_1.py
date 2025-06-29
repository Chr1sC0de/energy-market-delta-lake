from polars import String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int287_v4_gas_consumption_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int287_v4_gas_consumption_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "total_gas_used": String,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported (e.g. 30 Jun 2007)",
    "total_gas_used": "total gas used in gj",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
}

report_purpose = """
This public report shows the daily gas consumed  at an operational level and 
therefore will have minor discrepencies due ot metering substitutions or updates
post the gas day
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

from polars import Date, Datetime, Float64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import (
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int571_v4_latest_nsl_1"

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
    "nsl_update": Datetime(time_unit="ms", time_zone="UTC"),
    "network_name": String,
    "gas_date": Date,
    "distributor_name": String,
    "nsl_gj": Float64,
    "current_date": Datetime(time_unit="ms", time_zone="UTC"),
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
    group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
)

definitions_list.append(definition_builder.build())

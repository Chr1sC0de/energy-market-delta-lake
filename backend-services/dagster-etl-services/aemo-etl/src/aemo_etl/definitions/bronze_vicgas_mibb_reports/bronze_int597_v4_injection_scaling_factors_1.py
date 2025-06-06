from polars import Float64, Int64, String

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


table_name = "bronze_int597_v4_injection_scaling_factors_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int597_v4_injection_scaling_factors_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
    "gas_date",
    "distributor_name",
    "withdrawal_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "network_name": String,
    "version_id": Int64,
    "gas_date": String,
    "distributor_name": String,
    "withdrawal_zone": String,
    "scaling_factor": Float64,
    "current_date": String,
}

schema_descriptions = {
    "network_name": "Network name",
    "version_id": "Null for provisional statement type",
    "gas_date": "Gas date being reported. Format dd mmm yyyy e.g. 01 Jul 2007",
    "distributor_name": "Distribution Business name",
    "withdrawal_zone": "Withdrawal zone",
    "scaling_factor": "Injection scaling factor",
    "current_date": "Date and Time report produced 15 Aug 2007 10:06:54",
}

report_purpose = """
This report is produced for the settlement period and shows the scaling factor adjustments for aggregated injections in
Distribution region and withdrawal zone.

This public report shows the daily scaling factors used in adjusting the retailer injections to match the actual withdrawals in a
distribution region and withdrawal zone.
There is no equivalent VIC MIBB report.

Each report contents the:
- network name
- statement version identifier
- gas date
- distributor name
- withdrawal zone
- scaling factor
- current date
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

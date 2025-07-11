from polars import Float64, Int64, String

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

table_name = "bronze_int316_v4_operational_gas_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int316_v4_operational_gas_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "hv_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "hv_zone": Int64,
    "hv_zone_desc": String,
    "energy_gj": Float64,
    "volume_kscm": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Date the record was current, e.g. 30 Jun 2007",
    "hv_zone": "Heating value zone id number",
    "hv_zone_desc": "Heating value zone name",
    "energy_gj": "Sum of Hourly energy (GJ) for gas date",
    "volume_kscm": "Sum of Hourly volume (kscm) for gas date",
    "current_date": "Date and Time Report Produced, e.g. 30 Jun 2005 1:23:56",
}

report_purpose = """
This report is a comma separated values (csv) file that contains details of operational gas (volumes in kscm and energy in GJ)
by heating value zone.

This report should be used in conjunction with the linepack report to determine Market participant portion of operational gas.
Participants are advised to check the date range of the latest final settlement run to determine if the corresponding data in this
report is:
- provisional (no settlement version for the gas date)
- preliminary (only preliminary settlement has been run for the gas date)
- final (final settlement run for the gas date)
- revision (revision settlement has been run for the gas date)

This report is generated weekly on a Saturday.

Each report contains data for the period between and including the following:
The first gas date of the month that is 13 months prior to the current date and the gas date prior to the current gas date.
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

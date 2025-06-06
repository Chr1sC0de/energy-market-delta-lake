from polars import Int64, String

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


table_name = "bronze_int538_v4_settlement_versions_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int538_v4_settlement_versions_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "network_name": String,
    "version_id": Int64,
    "extract_type": String,
    "version_from_date": String,
    "version_to_date": String,
    "issued_date": String,
    "current_date": String,
}

schema_descriptions = {
    "network_name": "Network Name",
    "version_id": "balancing statement version (invoice_id) identifier",
    "extract_type": "P - Provisional, F - Final, R - Revision",
    "version_from_date": "Effective start date. (dd mmm yyyy)",
    "version_to_date": "Effective End date. (dd mmm yyyy)",
    "issued_date": "Issue date of settlement",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report is to display recently issued settlement versions when balancing statement is issued.
Participants may wish to use this report as a reference to link other reports together based on invoice id(balancing version).

A report is produced when balancing statement is issued.
This report is similar to VIC MIBB report INT438.

Each report contains the:
- statement version identifier
- settlement category type
- effective start date
- effective end date
- date of issue
- date and time when the report was produced
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

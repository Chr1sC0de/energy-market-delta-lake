from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int138_v4_settlement_version_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int138_v4_settlement_version_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "statement_version_id",
    "version_from_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "statement_version_id": Int64,
    "settlement_cat_type": String,
    "version_from_date": String,
    "version_to_date": String,
    "interest_rate": Float64,
    "issued_date": String,
    "version_desc": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "statement_version_id": "Statement version identifier",
    "settlement_cat_type": "Type (e.g. FNL for Final, PLM for Preliminary)",
    "version_from_date": "Effective start date (e.g. 30 Jun 2007)",
    "version_to_date": "Effective end date (e.g. 30 Jun 2007)",
    "interest_rate": "Interest rate applied to the settlement",
    "issued_date": "Date issued (e.g. 30 Jun 2007)",
    "version_desc": "Description of the version",
    "current_date": "Date and time report produced (e.g. 30 Jun 2007 06:00:00)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to display recently issued settlement versions.

Participants may wish to use this report as a reference to link other reports together based on settlement version.

A report is produced publicly when settlement statement is issued.

Each report contains the:
- statement version identifier
- settlement category type
- effective state date
- effective end date
- interest rate
- date of issue
- description of the version
- date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"

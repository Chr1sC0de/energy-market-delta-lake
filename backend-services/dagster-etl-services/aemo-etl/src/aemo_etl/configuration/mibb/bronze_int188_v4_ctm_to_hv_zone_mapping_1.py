from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int188_v4_ctm_to_hv_zone_mapping_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int188_v4_ctm_to_hv_zone_mapping_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "mirn",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "mirn": String,
    "site_company": String,
    "hv_zone": Int64,
    "hv_zone_desc": String,
    "effective_from": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "mirn": "Meter Installation Registration Number",
    "site_company": "Company name",
    "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",
    "hv_zone_desc": "Heating value zone name",
    "effective_from": "Date when the HV zone became effective for the mirn, Example: 01 Aug 2023",
    "current_date": "Date and time report produced, Example: 30 Jun 2007 06:00:00)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
A report containing the DWGM's Custody Transfer Meter (CTM) to Heating Value Zone mapping.

The report provides the mapping of active DTS CTMs to the Heating Value Zones. The mapping of non-DTS CTM to heating
value zone mapping for South Gippsland, Bairnsdale and Gippsland regions are also provided.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"

from polars import Datetime, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import (
    SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int898_v1_newstreetlisting_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int898_v1_newstreetlisting_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "distributor",
    "street_name",
    "suburb_or_place_or_locality",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "distributor": String,
    "street_name": String,
    "street_id": String,
    "street_suffix": String,
    "suburb_or_place_or_locality": String,
    "state_or_territory": String,
    "site_address_postcode": String,
    "current_date": Datetime(time_unit="ms", time_zone="UTC"),
}

schema_descriptions = {
    "distributor": "Hub profile ID of the distributor providing the data (e.g. AGLGNNWO)",
    "street_name": "Name of the street",
    "street_id": "Street identifier (if available)",
    "street_suffix": "Street suffix (if available)",
    "suburb_or_place_or_locality": "Suburb, place or locality name",
    "state_or_territory": "State or territory (if available)",
    "site_address_postcode": "Postcode (if available)",
    "current_date": "Report creation date and timestamp",
}

report_purpose = """
This report provides a listing of all street/suburb combinations where the distributor is the current distributor.

AEMO processes files sent by distributors and publishes the new street listing data via this public MIBB report.
This process is applicable to NSW/ACT networks.

The 'New Street Listing Report' is a CSV report listing all street/suburb combinations where the distributor is the current distributor.
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
    time_zone="Australia/Canberra",
    group_name=f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}",
)

definitions_list.append(definition_builder.build())

from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Facility Developments report              │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_facility_developments"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbfacilitydevelopments*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "DevFacilityId",
    "EffectiveDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "DevFacilityId": Int64,
    "ProposedName": String,
    "EffectiveDate": String,
    "FacilityType": String,
    "MinNameplate": Float64,
    "MaxNameplate": Float64,
    "Location": String,
    "PlannedCommissionFrom": String,
    "PlannedCommissionTo": String,
    "DevelopmentStage": String,
    "RelatedFacilityId": Int64,
    "RelatedFacilityName": String,
    "Comments": String,
    "ReportingEntity": String,
}

schema_descriptions = {
    "DevFacilityId": "A unique AEMO defined Development Facility Identifier.",
    "ProposedName": "The name of the Facility development.",
    "EffectiveDate": "The effective date of the submission.",
    "FacilityType": "The facility development type.",
    "MinNameplate": "The lower estimate of nameplate rating capacity.",
    "MaxNameplate": "The upper estimate of nameplate rating capacity.",
    "Location": "The location of the development facility.",
    "PlannedCommissionFrom": "The planned start date of commissioning.",
    "PlannedCommissionTo": "The planned end date of commissioning.",
    "DevelopmentStage": "The current stage of the development facility being, PROPOSED, COMMITTED, CANCELLED, ENDED.",
    "RelatedFacilityId": "Any facility ID's related to the development facility.",
    "RelatedFacilityName": "The name of any facility ID's related to the development facility.",
    "Comments": "Any additional comments included in the submission.",
    "ReportingEntity": "The entity who is reporting for the facility development.",
}

report_purpose = """
This report displays a list of all Facility Developments.

GASBB_FACILITYDEVELOPMENTS is generally updated within 30 minutes of receiving new data.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

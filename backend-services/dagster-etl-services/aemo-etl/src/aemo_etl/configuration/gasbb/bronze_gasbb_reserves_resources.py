from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Reserves And Resources report             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_reserves_resources"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbreservesandresources*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FieldId",
    "FieldInterestId",
    "EffectiveDate",
    "VersionDateTime",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "FieldId": Int64,
    "FieldName": String,
    "FieldInterestId": Int64,
    "DevelopedReserve1P": Float64,
    "DevelopedReserve2P": Float64,
    "DevelopedReserve3P": Float64,
    "UndevelopedReserve1P": Float64,
    "UndevelopedReserve2P": Float64,
    "UndevelopedReserve3P": Float64,
    "Resources2C": Float64,
    "ProductionChangeReserve2P": Float64,
    "ProvedAreaExtensionReserve2P": Float64,
    "PercentageChangeReserve2P": Float64,
    "UpwardRevisionFrom3PReserveTo2P": Float64,
    "DownwardRevisionFrom2PReserveTo3P": Float64,
    "OtherRevisionsReserve2P": Float64,
    "MaturitySubClass2P": String,
    "MaturitySubClass2C": String,
    "MinDate2P": String,
    "MaxDate2P": String,
    "MinDate2C": String,
    "MaxDate2C": String,
    "ExpectedBarriers2C": String,
    "ResourcesEstimateMethod": String,
    "ConversionFactorQtyTCFtoPJ": Float64,
    "EconomicAssumption": String,
    "UpdateReason": String,
    "PreparedBy": String,
    "PreparationIndependenceStatement": String,
    "EffectiveDate": String,
    "VersionDateTime": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "FieldId": "A unique AEMO defined Field Identifier.",
    "FieldName": "The name of the field.",
    "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
    "DevelopedReserve1P": "An estimate of the BB field interest's 1P developed reserves.",
    "DevelopedReserve2P": "An estimate of the BB field interest's 2P developed reserves.",
    "DevelopedReserve3P": "An estimate of the BB field interest's 3P developed reserves.",
    "UndevelopedReserve1P": "An estimate of the BB field interest's 1P undeveloped reserves.",
    "UndevelopedReserve2P": "An estimate of the BB field interest's 2P undeveloped reserves.",
    "UndevelopedReserve3P": "An estimate of the BB field interest's 3P undeveloped reserves.",
    "Resources2C": "An estimate of the BB field interest's 2C resources.",
    "ProductionChangeReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to the production of gas.",
    "ProvedAreaExtensionReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to the extension of a field's proved area.",
    "PercentageChangeReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to a percentage change in the BB field interest.",
    "UpwardRevisionFrom3PReserveTo2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to an upward revision of 2P reserves arising from the reclassification of 3P reserves or resources to 2P reserves.",
    "DownwardRevisionFrom2PReserveTo3P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to a downward revision of 2P reserves arising from the reclassification of 2P reserves to 3P reserves or resources.",
    "OtherRevisionsReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to other revisions.",
    "MaturitySubClass2P": "The project maturity sub-class for the 2P reserves.",
    "MaturitySubClass2C": "The project maturity sub-class for the 2C resources.",
    "MinDate2P": "The earliest estimated date for the production of the 2P reserves.",
    "MaxDate2P": "The latest estimated date for the production of the 2P reserves.",
    "MinDate2C": "The earliest estimated date for the production of the 2C resources.",
    "MaxDate2C": "The latest estimated date for the production of the 2C resources.",
    "ExpectedBarriers2C": "A list of any barriers to the commercial recovery of the 2C resources.",
    "ResourcesEstimateMethod": "The resources assessment method used to prepare the reserves and resources estimates.",
    "ConversionFactorQtyTCFtoPJ": "The conversion factor used to convert quantities measured in trillions of cubic feet to PJ.",
    "EconomicAssumption": "The key economic assumptions in the forecast case used to prepare the reserves and resources estimates and the source of the assumptions.",
    "UpdateReason": "The reason for the update.",
    "PreparedBy": "The name of the person who prepared the estimates.",
    "PreparationIndependenceStatement": "Whether the qualified gas industry professional who prepared, or supervised the preparation of, the reserves and resources estimates is independent of the BB reporting entity.",
    "EffectiveDate": "The date on which the record takes effect.",
    "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report displays information about Field Reserves and Resources.

Both GASBB_2P_SENSETIVITIES_ALL and GASBB_2P_SENSETIVITIES_LAST_QUARTER are updated monthly.

Contains all current reserve and resource information for a BB field interest.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"

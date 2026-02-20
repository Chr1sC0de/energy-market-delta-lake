"""bronze_gasbb_reserves_resources - Bronze GASBB report configuration."""

from polars import String, Int64, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_reserves_resources",
        s3_file_glob="gasbbreservesandresources*",
        primary_keys=["FieldId", "FieldInterestId", "EffectiveDate", "VersionDateTime"],
        table_schema={
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
        },
        schema_descriptions={
            "FieldId": "A unique AEMO defined Field Identifier.",
            "FieldName": "The name of the field.",
            "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
            "DevelopedReserve1P": "An estimate of the BB field interest's 1P developed reserves.",  # noqa: E501
            "DevelopedReserve2P": "An estimate of the BB field interest's 2P developed reserves.",  # noqa: E501
            "DevelopedReserve3P": "An estimate of the BB field interest's 3P developed reserves.",  # noqa: E501
            "UndevelopedReserve1P": "An estimate of the BB field interest's 1P undeveloped reserves.",  # noqa: E501
            "UndevelopedReserve2P": "An estimate of the BB field interest's 2P undeveloped reserves.",  # noqa: E501
            "UndevelopedReserve3P": "An estimate of the BB field interest's 3P undeveloped reserves.",  # noqa: E501
            "Resources2C": "An estimate of the BB field interest's 2C resources.",
            "ProductionChangeReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to the production of gas.",  # noqa: E501
            "ProvedAreaExtensionReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to the extension of a field's proved area.",  # noqa: E501
            "PercentageChangeReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to a percentage change in the BB field interest.",  # noqa: E501
            "UpwardRevisionFrom3PReserveTo2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to an upward revision of 2P reserves arising from the reclassification of 3P reserves or resources to 2P reserves.",  # noqa: E501
            "DownwardRevisionFrom2PReserveTo3P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to a downward revision of 2P reserves arising from the reclassification of 2P reserves to 3P reserves or resources.",  # noqa: E501
            "OtherRevisionsReserve2P": "An estimate of the total movement in the BB field interest's 2P reserves since the end of prior reporting year due to other revisions.",  # noqa: E501
            "MaturitySubClass2P": "The project maturity sub-class for the 2P reserves.",
            "MaturitySubClass2C": "The project maturity sub-class for the 2C resources.",  # noqa: E501
            "MinDate2P": "The earliest estimated date for the production of the 2P reserves.",  # noqa: E501
            "MaxDate2P": "The latest estimated date for the production of the 2P reserves.",  # noqa: E501
            "MinDate2C": "The earliest estimated date for the production of the 2C resources.",  # noqa: E501
            "MaxDate2C": "The latest estimated date for the production of the 2C resources.",  # noqa: E501
            "ExpectedBarriers2C": "A list of any barriers to the commercial recovery of the 2C resources.",  # noqa: E501
            "ResourcesEstimateMethod": "The resources assessment method used to prepare the reserves and resources estimates.",  # noqa: E501
            "ConversionFactorQtyTCFtoPJ": "The conversion factor used to convert quantities measured in trillions of cubic feet to PJ.",  # noqa: E501
            "EconomicAssumption": "The key economic assumptions in the forecast case used to prepare the reserves and resources estimates and the source of the assumptions.",  # noqa: E501
            "UpdateReason": "The reason for the update.",
            "PreparedBy": "The name of the person who prepared the estimates.",
            "PreparationIndependenceStatement": "Whether the qualified gas industry professional who prepared, or supervised the preparation of, the reserves and resources estimates is independent of the BB reporting entity.",  # noqa: E501
            "EffectiveDate": "The date on which the record takes effect.",
            "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays information about Field Reserves and Resources.\n\nBoth GASBB_2P_SENSETIVITIES_ALL and GASBB_2P_SENSETIVITIES_LAST_QUARTER are updated monthly.\n\nContains all current reserve and resource information for a BB field interest.\n",  # noqa: E501
    )

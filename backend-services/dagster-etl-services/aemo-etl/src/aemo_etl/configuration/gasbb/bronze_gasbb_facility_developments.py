"""bronze_gasbb_facility_developments - Bronze GASBB report configuration."""

from polars import String, Int64, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_facility_developments",
        s3_file_glob="gasbbfacilitydevelopments*",
        primary_keys=["DevFacilityId", "EffectiveDate"],
        table_schema={
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
            "RelatedFacilityId": String,
            "RelatedFacilityName": String,
            "Comments": String,
            "ReportingEntity": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "DevFacilityId": "A unique AEMO defined Development Facility Identifier.",
            "ProposedName": "The name of the Facility development.",
            "EffectiveDate": "The effective date of the submission.",
            "FacilityType": "The facility development type.",
            "MinNameplate": "The lower estimate of nameplate rating capacity.",
            "MaxNameplate": "The upper estimate of nameplate rating capacity.",
            "Location": "The location of the development facility.",
            "PlannedCommissionFrom": "The planned start date of commissioning.",
            "PlannedCommissionTo": "The planned end date of commissioning.",
            "DevelopmentStage": "The current stage of the development facility being, PROPOSED, COMMITTED, CANCELLED, ENDED.",  # noqa: E501
            "RelatedFacilityId": "Any facility ID's related to the development facility.",  # noqa: E501
            "RelatedFacilityName": "The name of any facility ID's related to the development facility.",  # noqa: E501
            "Comments": "Any additional comments included in the submission.",
            "ReportingEntity": "The entity who is reporting for the facility development.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays a list of all Facility Developments.\n\nGASBB_FACILITYDEVELOPMENTS is generally updated within 30 minutes of receiving new data.\n",  # noqa: E501
    )

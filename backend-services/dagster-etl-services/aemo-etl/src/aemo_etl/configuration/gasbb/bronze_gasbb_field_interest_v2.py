"""bronze_gasbb_field_interest_v2 - Bronze GASBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_field_interest_v2",
        s3_file_glob="gasbbgasfieldinterest*",
        primary_keys=["FieldInterestId", "CompanyId", "EffectiveDate"],
        table_schema={
            "FieldName": String,
            "FieldInterestId": Int64,
            "CompanyId": Int64,
            "CompanyName": String,
            "GroupMembers": String,
            "PercentageShare": String,
            "EffectiveDate": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FieldName": "The name of the Field in which the Field Interest is located.",  # noqa: E501
            "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
            "CompanyId": "The company ID of the responsible participant.",
            "CompanyName": "The company name of the responsible participant.",
            "GroupMembers": "The name of the group member.",
            "PercentageShare": "The BB field interest (as a percentage) of each member of the field owner group.",  # noqa: E501
            "EffectiveDate": "The date on which the record takes effect.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays information about Field Interests.\n\nGASBB_FIELD_INTEREST is updated daily.\n",  # noqa: E501
    )

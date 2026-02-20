"""bronze_gasbb_late_nomination_forecast - Bronze GASBB report configuration."""

from polars import String, Int64, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_late_nomination_forecast",
        s3_file_glob="gasbblatenominationandforecast*",
        primary_keys=[
            "GasDate",
            "FacilityId",
            "ConnectionPointId",
            "EarliestSubmissionDate",
        ],
        table_schema={
            "GasDate": String,
            "FacilityName": String,
            "FacilityId": Int64,
            "ConnectionPointId": Int64,
            "EarliestSubmissionDate": String,
            "LateTimeSpan": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityName": "Name of the facility.",
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "EarliestSubmissionDate": "Date and time of the earliest submission for that gas date.",  # noqa: E501
            "LateTimeSpan": "Hours and minutes of the time span between the submission cut-off time and the earliest submission date.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nA record of late submissions for BB reporting entities for each BB facility type.\n\nGASBB_LATE_NOMINATION_AND_FORECAST is updated daily.\n\nThe report covers the last 31 days.\n",  # noqa: E501
    )

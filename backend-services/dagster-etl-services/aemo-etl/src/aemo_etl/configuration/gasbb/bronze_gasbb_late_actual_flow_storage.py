"""bronze_gasbb_late_actual_flow_storage - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_late_actual_flow_storage",
        s3_file_glob="gasbblateactualflowandstorage*",
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
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
            "FacilityName": "Name of the facility.",
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "EarliestSubmissionDate": "Date and time of the earliest submission for that gas date.",
            "LateTimeSpan": "Hours and minutes of the time span between the submission cut-off time and the earliest submission date.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nA record of late submissions.\n\nGASBB_LATE_ACTUAL_FLOW_AND_STORAGE is updated daily.\n\nThe report covers the last 31 days.\n",
    )

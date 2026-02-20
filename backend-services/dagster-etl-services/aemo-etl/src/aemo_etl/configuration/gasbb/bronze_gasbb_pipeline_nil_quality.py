"""bronze_gasbb_pipeline_nil_quality - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_pipeline_nil_quality",
        s3_file_glob="gasbbpipelinenilqualitysubmission*",
        primary_keys=["GasDate", "FacilityId", "ConnectionPointId"],
        table_schema={
            "GasDate": String,
            "FacilityName": String,
            "FacilityId": Int64,
            "ConnectionPointId": Int64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityName": "Name of the facility.",
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nA record of all submissions that contain Nil quality against the flow. This indicates that data wasn't available and needs to be updated.\n\nGASBB_PIPELINE_NIL_QUALITY_SUBMISSION is updated daily.\n\nContains all current records of gas flow submissions with Nil quality.\n",  # noqa: E501
    )

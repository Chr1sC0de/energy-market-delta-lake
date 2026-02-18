"""bronze_gasbb_missing_actual_flow_storage - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_missing_actual_flow_storage",
        s3_file_glob="gasbbmissingactualflowandstorage*",
        primary_keys=["GasDate", "FacilityId", "ConnectionPointId"],
        table_schema={
            "GasDate": String,
            "FacilityName": String,
            "FacilityId": Int64,
            "ConnectionPointId": Int64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
            "FacilityName": "Name of the facility.",
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nReturns any missing actual flow data.\n\nGASBB_MISSING_ACTUAL_FLOW_AND_STORAGE is updated daily.\n\nThe report covers the last 31 days.\n",
    )

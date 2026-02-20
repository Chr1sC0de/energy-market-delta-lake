"""bronze_gasbb_pipeline_connection_flow_v2 - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_pipeline_connection_flow_v2",
        s3_file_glob="gasbbpipelineconnectionflow*",
        primary_keys=[
            "GasDate",
            "FacilityId",
            "ConnectionPointId",
            "FlowDirection",
            "LastUpdated",
        ],
        table_schema={
            "GasDate": String,
            "FacilityName": String,
            "FacilityId": Int64,
            "ConnectionPointName": String,
            "ConnectionPointId": Int64,
            "ActualQuantity": Float64,
            "FlowDirection": String,
            "State": String,
            "LocationName": String,
            "LocationId": Int64,
            "Quality": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "FacilityName": "Name of the facility.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "ConnectionPointName": "Names of the connection point.",
            "FlowDirection": "A conditional value of either: RECEIPT — A flow of gas into the BB pipeline, or DELIVERY — A flow of gas out of the BB pipeline.",  # noqa: E501
            "ActualQuantity": "The actual flow quantity reported in TJ to the nearest terajoule with three decimal places.",  # noqa: E501
            "State": "Location.",
            "LocationName": "Name of the Location.",
            "LocationId": "Unique Location identifier.",
            "Quality": "Indicates whether meter data for the submission date is available. Values can be either: OK, NIL, OOR, Not Available.",  # noqa: E501
            "LastUpdated": "Date and time the record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nProvides a report for the Daily production and usage at each Connection Point.\n\nGASBB_PIPELINE_CONNECTION_FLOW is updated daily.\nGASBB_PIPELINE_CONNECTION_FLOW_LAST_31 is typically updated within 30 minutes of receiving new data.\n\nGASBB_PIPELINE_CONNECTION_FLOW contains historical data from Sep 2018.\nGASBB_PIPELINE_CONNECTION_FLOW_LAST_31 contains data from the last 31 days.\n",  # noqa: E501
    )

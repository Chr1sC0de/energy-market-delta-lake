"""bronze_gasbb_demand_zones_and_pipeline_connectionpoint_mapping - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_demand_zones_and_pipeline_connectionpoint_mapping",
        s3_file_glob="gasbbdemandzonespipelineconnectionpointmapping*",
        primary_keys=["FacilityId", "NodeId", "ConnectionPointId", "FlowDirection"],
        table_schema={
            "FacilityName": String,
            "FacilityType": String,
            "FacilityId": Int64,
            "NodeId": Int64,
            "ConnectionPointId": Int64,
            "FlowDirection": String,
            "ConnectionPointName": String,
            "State": String,
            "DemandZone": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FacilityName": "Name of the facility.",
            "FacilityType": "The facility development type.",
            "FacilityId": "The gas storage facility ID for the facility by means of which the service is provided.",
            "NodeId": "A unique AEMO defined node identifier.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "FlowDirection": "Gas flow direction. Values can be: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",
            "ConnectionPointName": "Names of the connection point.",
            "State": "The state where the transaction occurred.",
            "DemandZone": "",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nProvides mapping between pipelines, connectionpoints and  demand zones:w\n",
    )

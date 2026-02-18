"""bronze_gasbb_nodes_connection_points - Bronze GASBB report configuration."""

from polars import Boolean, String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_nodes_connection_points",
        s3_file_glob="gasbbnodesandconnectionpoints*",
        primary_keys=[
            "FacilityId",
            "ConnectionPointId",
            "EffectiveDate",
            "LastUpdated",
        ],
        table_schema={
            "FacilityName": String,
            "FacilityId": Int64,
            "FacilityType": String,
            "ConnectionPointId": Int64,
            "ConnectionPointName": String,
            "FlowDirection": String,
            "Exempt": Boolean,
            "ExemptionDescription": String,
            "NodeId": Int64,
            "StateId": Int64,
            "StateName": String,
            "LocationName": String,
            "LocationId": Int64,
            "EffectiveDate": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FacilityName": "Name of the facility.",
            "FacilityId": "A unique AEMO defined facility identifier.",
            "FacilityType": "Facility type associated with the Facility Id.",
            "ConnectionPointId": "A unique AEMO defined connection point identifier.",
            "ConnectionPointName": "Name of connection point.",
            "FlowDirection": "Gas flow direction. Values can be either: Receipt, Delivery, Processed, or DeliveryLngStor.",
            "Exempt": "Flag indicating whether the connection point has a data exemption.",
            "ExemptionDescription": "Description of exemption.",
            "NodeId": "A unique AEMO defined node identifier.",
            "StateId": "A unique AEMO defined state identifier.",
            "StateName": "Name of the state.",
            "LocationName": "Name of location.",
            "LocationId": "A unique AEMO defined location identifier.",
            "EffectiveDate": "Date record is effective from",
            "LastUpdated": "Date the record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nDisplays detailed information on all facilities and their associated nodes and Connection Points.\n\nBoth GASBB_NODES_AND_CONNECTIONPOINTS_LIST and GASBB_NODES_CONNECTIONPOINTS_FULL_LIST are updated daily.\n\nContains all current facilities and their nodes and connection points.\n",
    )

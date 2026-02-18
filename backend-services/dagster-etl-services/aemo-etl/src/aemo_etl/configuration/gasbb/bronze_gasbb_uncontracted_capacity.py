"""bronze_gasbb_uncontracted_capacity - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_uncontracted_capacity",
        s3_file_glob="gasbbuncontractedcapacity*",
        primary_keys=[
            "FacilityId",
            "OutlookMonth",
            "OutlookYear",
            "CapacityType",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "FacilityType",
            "LastUpdated",
        ],
        table_schema={
            "FacilityId": Int64,
            "FacilityName": String,
            "FacilityType": String,
            "OutlookMonth": Int64,
            "OutlookYear": Int64,
            "CapacityType": String,
            "OutlookQuantity": Float64,
            "FlowDirection": String,
            "CapacityDescription": String,
            "ReceiptLocation": Int64,
            "ReceiptLocationName": String,
            "DeliveryLocation": Int64,
            "DeliveryLocationName": String,
            "Description": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FacilityId": "Unique plant identifier.",
            "FacilityName": "Name of the plant.",
            "FacilityType": "Facility type associated with the Facility Id.",
            "OutlookMonth": "The month that the uncontracted capacity is available.",
            "OutlookYear": "The year that the uncontracted capacity is available.",
            "CapacityType": "Capacity type can be either: Storage: Holding capacity in storage, or MDQ: Uncontracted primary firm capacity on the BB facility.",
            "OutlookQuantity": "Outlook Quantity as the daily average quantity across the month in TJ to three decimal places.",
            "FlowDirection": "Gas flow direction. Values can be either: RECEIPT — A flow of gas into the BB facility, or DELIVERY — A flow of gas out of the BB facility.",
            "CapacityDescription": "Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information.",
            "ReceiptLocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location.",
            "ReceiptLocationName": "The name of the receipt location.",
            "DeliveryLocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location.",
            "DeliveryLocationName": "The name of the delivery location.",
            "Description": "Comments about the quantity or change in Outlook Quantity relating to the Facility Id, and the times, dates, or duration which those quantities or changes in quantities.",
            "LastUpdated": "Date and time record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides information on the Uncontracted primary firm capacity outlook on BB pipelines, \nBB storage, BB compression, BB Production and LNG import facilities for the next 36 months.\n\nGASBB_UNCONTRACTED_CAPACITY_FULL_LIST is updated monthly.\nGASBB_UNCONTRACTED_CAPACITY_FUTURE is generally updated within 30 minutes of receiving new data.\n\nGASBB_UNCONTRACTED_CAPACITY_FULL_LIST contains historical records.\nGASBB_UNCONTRACTED_CAPACITY_FUTURE contains only future looking outlooks.\n",
    )

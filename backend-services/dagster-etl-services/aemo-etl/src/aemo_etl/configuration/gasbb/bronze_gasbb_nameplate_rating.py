"""bronze_gasbb_nameplate_rating - Bronze GASBB report configuration."""

from polars import String, Int64, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_nameplate_rating",
        s3_file_glob="gasbbnameplaterating*",
        primary_keys=[
            "facilityid",
            "capacitytype",
            "flowdirection",
            "effectivedate",
            "lastupdated",
        ],
        table_schema={
            "facilityname": String,
            "facilityid": Int64,
            "facilitytype": String,
            "capacitytype": String,
            "capacityquantity": Float64,
            "flowdirection": String,
            "capacitydescription": String,
            "receiptlocation": Int64,
            "receiptlocationName": String,
            "deliverylocation": Int64,
            "deliverylocationName": String,
            "effectivedate": String,
            "description": String,
            "lastupdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "facilityname": "Facility name associated with the Facility Id.",
            "facilityid": "A unique AEMO defined Facility identifier.",
            "facilitytype": "Facility type associated with the Facility Id.",
            "capacitytype": "Capacity type can be either: Storage: Holding capacity in storage, or MDQ: Daily maximum firm capacity (name plate) under the expected operating conditions.",
            "capacityquantity": "Standing capacity quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",
            "flowdirection": "Gas flow direction. Values can be either: Receipt, Delivery, Processed, DeliveryLngStor, or NONE.",
            "capacitydescription": "Free text to describe the meaning of the capacity number provided, including relevant assumptions made in the calculation of the capacity number and any other relevant information.",
            "receiptlocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location.",
            "receiptlocationName": "The name of the receipt location.",
            "deliverylocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location.",
            "deliverylocationName": "The name of the delivery location.",
            "effectivedate": "Gas day date that corresponding record takes effect. Any time component supplied will be ignored.",
            "description": "Free text facility use is restricted to a description for reasons or comments directly related to the quantity or the change in quantity provided in relation to a BB facility.",
            "lastupdated": "Date and time record was last updated.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report displays the standing nameplate capacity of all BB facilities and BB compression facility. Nameplate rating relates to maximum daily quantities in TJ under normal operating conditions.\n\nGASBB_NAMEPLATE_RATING_FULL_LIST is updated annually / GASBB_NAMEPLATE_RATING_CURRENT is updated within 30 minutes of receiving new data.\n\nGASBB_NAMEPLATE_RATING_FULL_LIST contains historical records / GASBB_NAMEPLATE_RATING_CURRENT contains the current nameplate.\n",
    )

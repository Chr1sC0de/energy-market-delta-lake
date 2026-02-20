"""bronze_gasbb_medium_term_capacity_outlook - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_medium_term_capacity_outlook",
        s3_file_glob="gasbbmediumtermcapacityoutlook*",
        primary_keys=[
            "FromGasDate",
            "ToGasDate",
            "FacilityId",
            "CapacityType",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "LastUpdated",
        ],
        table_schema={
            "FacilityId": Int64,
            "FacilityName": String,
            "FromGasDate": String,
            "ToGasDate": String,
            "CapacityType": String,
            "OutlookQuantity": Float64,
            "FlowDirection": String,
            "CapacityDescription": String,
            "ReceiptLocation": Int64,
            "DeliveryLocation": Int64,
            "ReceiptLocationName": String,
            "DeliveryLocationName": String,
            "Description": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FacilityId": "Unique plant identifier.",
            "FacilityName": "Name of the plant.",
            "FromGasDate": "Date of gas day. Any time component supplied is ignored. The gas day is applicable under the pipeline contract or market rules.",  # noqa: E501
            "ToGasDate": "Date of gas day. Any time component supplied is ignored. The gas day is that applicable under the pipeline contract or market rules.",  # noqa: E501
            "CapacityType": "Capacity type values can be: STORAGE — Holding capacity in storage; or MDQ — Daily maximum firm capacity under the expected operating conditions.",  # noqa: E501
            "OutlookQuantity": "Capacity outlook quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",  # noqa: E501
            "FlowDirection": "Gas flow direction. Values can be: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",  # noqa: E501
            "CapacityDescription": "Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information. Will only be shown for Pipelines, Compression facilities and may be shown for LNGImport facilities.",  # noqa: E501
            "ReceiptLocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location. Note: Applicable to BB pipelines only. For other BB facilities, this field is populated with -1.",  # noqa: E501
            "DeliveryLocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location. Note: Applicable to BB pipelines only. For other BB facilities, this field is populated with -1.",  # noqa: E501
            "ReceiptLocationName": "The name of the receipt location.",
            "DeliveryLocationName": "The name of the delivery location.",
            "Description": "Comments about the quantity or change in Outlook Quantity relating to the Facility Id, and the times, dates, or duration which those quantities or changes in quantities.",  # noqa: E501
            "LastUpdated": "Date and time record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nProvides a report of the Capacity Outlook for the medium term to identify possible impact to future supply.\n\nTwo report types exist:\n- GASBB_MEDIUM_TERM_OUTLOOK_FULL_LIST: Contains historic and future outlooks, updated daily.\n- GASBB_MEDIUM_TERM_OUTLOOK_FUTURE: Contains the current and future outlooks, updated within 30 minutes of receiving new data.\n\nEach record represents the outlook for one facility, for a range of gas days (FromGasDate to ToGasDate), for one type of capacity, and a given flow direction.\n\nThe report supports understanding medium-term constraints or capacities on gas facilities such as pipelines, storage, and LNG.\n",  # noqa: E501
    )

"""bronze_gasbb_short_term_capacity_outlook - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_short_term_capacity_outlook",
        s3_file_glob="gasbbshorttermcapacityoutlook*",
        primary_keys=[
            "GasDate",
            "FacilityId",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "LastUpdated",
        ],
        table_schema={
            "GasDate": String,
            "FacilityId": Int64,
            "FacilityName": String,
            "CapacityType": String,
            "CapacityTypeDescription": String,
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
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityId": "A unique AEMO defined Facility Identifier.",
            "FacilityName": "The name of the BB facility.",
            "CapacityType": "STORAGE — Holding capacity; MDQ — Daily max firm capacity under expected conditions.",  # noqa: E501
            "CapacityTypeDescription": "Description of the capacity type (e.g. daily max firm capacity under expected conditions).",  # noqa: E501
            "OutlookQuantity": "Capacity outlook quantity to 3 decimal places.",
            "FlowDirection": "Direction of gas flow: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",  # noqa: E501
            "CapacityDescription": "Free text describing meaning of capacity number and material factors (for pipelines/compressors).",  # noqa: E501
            "ReceiptLocation": "Connection Point ID representing the receipt location. -1 for non-pipeline facilities.",  # noqa: E501
            "DeliveryLocation": "Connection Point ID representing the delivery location. -1 for non-pipeline facilities.",  # noqa: E501
            "ReceiptLocationName": "Description of the Receipt Location (BB pipelines only).",  # noqa: E501
            "DeliveryLocationName": "Description of the Delivery Location (BB pipelines only).",  # noqa: E501
            "Description": "Comments about quantity or changes, timing, dates or durations relating to the record.",  # noqa: E501
            "LastUpdated": "Timestamp of last modification.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays the expected daily capacity of a BB facility for the next seven days. It helps traders and market \nparticipants to understand projected network capabilities and restrictions.\n\nTwo report types exist:\n- GASBB_SHORT_TERM_CAPACITY_OUTLOOK: Historical outlooks updated daily.\n- GASBB_SHORT_TERM_CAPACITY_OUTLOOK_FUTURE: Forecast data updated within 30 minutes of new input.\n\nEach record represents the outlook for one facility, on one gas day, for one type of capacity, and a given flow direction.\n\nThe report supports understanding short-term constraints or capacities on gas facilities such as pipelines, storage, and LNG.\n",  # noqa: E501
    )

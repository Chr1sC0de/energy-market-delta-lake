"""bronze_gasbb_facilities - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_facilities",
        s3_file_glob="gasbbfacilities*",
        primary_keys=["FacilityId", "LastUpdated"],
        table_schema={
            "FacilityName": String,
            "FacilityShortName": String,
            "FacilityId": Int64,
            "FacilityType": String,
            "FacilityTypeDescription": String,
            "OperatingState": String,
            "OperatingStateDate": String,
            "OperatorName": String,
            "OperatorId": Int64,
            "OperatorChangeDate": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "FacilityName": "Name of the facility.",
            "FacilityShortName": "Abbreviated version of the facility name.",
            "FacilityId": "A unique AEMO defined facility identifier.",
            "FacilityType": "Facility type associated with the facility id.",
            "FacilityTypeDescription": "Free text description of the facility type.",
            "OperatingState": "The operating state (Active or Inactive) of the facility.",  # noqa: E501
            "OperatingStateDate": "Date the current operating state was set.",
            "OperatorName": "Name of the operator for the facility.",
            "OperatorId": "The facility operator's ID.",
            "OperatorChangeDate": "Date the current operator for the facility was set.",
            "LastUpdated": "Date and time the record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nDisplays a list of all currently registered BB facilities and identifies the organisation responsible for the operation of the respective facility.\n\nBoth GASBB_FACILITIES_LIST and GASBB_FACILITIES_FULL_LIST are updated daily.\n\nCurrent records.\n",  # noqa: E501
    )

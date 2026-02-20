"""bronze_gasbb_locations_list - Bronze GASBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_locations_list",
        s3_file_glob="gasbblocationslist*",
        primary_keys=["LocationId", "LastUpdated"],
        table_schema={
            "LocationName": String,
            "LocationId": Int64,
            "State": String,
            "LocationType": String,
            "Description": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "LocationName": "Name of the Location.",
            "LocationId": "Unique Location identifier.",
            "State": "Location state.",
            "LocationType": "Type of location.",
            "Description": "Free text description of the Location including boundaries and the basis of measurement.",  # noqa: E501
            "LastUpdated": "Date the list of locations was last updated.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report lists all production and demand locations within the Bulletin Board system.\n\nThis report is updated daily and shows current records.\n",  # noqa: E501
    )

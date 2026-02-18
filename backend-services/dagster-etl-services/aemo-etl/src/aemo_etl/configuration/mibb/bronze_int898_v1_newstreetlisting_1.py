"""bronze_int898_v1_newstreetlisting_1 - Bronze MIBB report configuration."""

from polars import String

from aemo_etl.configuration import SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int898_v1_newstreetlisting_1",
        s3_file_glob="int898_v1_newstreetlisting_1*",
        primary_keys=["distributor", "street_name", "suburb_or_place_or_locality"],
        table_schema={
            "distributor": String,
            "street_name": String,
            "street_id": String,
            "street_suffix": String,
            "suburb_or_place_or_locality": String,
            "state_or_territory": String,
            "site_address_postcode": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "distributor": "Hub profile ID of the distributor providing the data (e.g. AGLGNNWO)",
            "street_name": "Name of the street",
            "street_id": "Street identifier (if available)",
            "street_suffix": "Street suffix (if available)",
            "suburb_or_place_or_locality": "Suburb, place or locality name",
            "state_or_territory": "State or territory (if available)",
            "site_address_postcode": "Postcode (if available)",
            "current_date": "Report creation date and timestamp",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides a listing of all street/suburb combinations where the distributor is the current distributor.\n\nAEMO processes files sent by distributors and publishes the new street listing data via this public MIBB report.\nThis process is applicable to NSW/ACT networks.\n\nThe 'New Street Listing Report' is a CSV report listing all street/suburb combinations where the distributor is the current distributor.\n",
        group_name=f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}",
    )

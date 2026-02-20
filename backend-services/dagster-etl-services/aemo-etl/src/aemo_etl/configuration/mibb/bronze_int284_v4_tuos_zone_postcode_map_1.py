"""bronze_int284_v4_tuos_zone_postcode_map_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int284_v4_tuos_zone_postcode_map_1",
        s3_file_glob="int284_v4_tuos_zone_postcode_map_1*",
        primary_keys=["postcode", "tuos_zone"],
        table_schema={
            "last_update_datetime": String,
            "postcode": String,
            "tuos_zone": Int64,
            "tuos_zone_desc": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "last_update_datetime": "date time the mapping was last updated in AEMO database (e.g. 30 Jun 2007)",  # noqa: E501
            "postcode": "Post Code",
            "tuos_zone": "TUOS Zone mapped to post code",
            "tuos_zone_desc": "TUoS Zone description",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis public report defines the postcodes to TUoS zone mappings used to assign new MIRNs to a TUoS zone for TUoS billing\npurposes. It is this mapping that is provided to the Transmission System Service Provider for billing purposes. Retail\nbusinesses can use this report to verify the MIRNs that are being billed in each TUoS zone, and also to confirm the DB\nNetwork to which it is connected and the heating Zone used if it is an interval meter.\n\nA report is produced monthly showing the current transmission tariff zone to postcode mapping.\nThe report only covers the DTS (declared transmission system) network.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

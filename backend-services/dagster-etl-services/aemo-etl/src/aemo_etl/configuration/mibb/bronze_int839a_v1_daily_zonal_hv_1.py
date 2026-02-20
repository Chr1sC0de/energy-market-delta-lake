"""bronze_int839a_v1_daily_zonal_hv_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int839a_v1_daily_zonal_hv_1",
        s3_file_glob="int839a_v1_daily_zonal_hv_1*",
        primary_keys=["gas_date", "hv_zone"],
        table_schema={
            "gas_date": String,
            "hv_zone": Int64,
            "hv_zone_description": String,
            "heating_value_mj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 30 Jun 2007. Covering a period of 120 gas days (as available).",  # noqa: E501
            "hv_zone": "Heating value zone as assigned by the distributor",
            "hv_zone_description": "Name of the heating value zone",
            "heating_value_mj": "The Heating value is in MJ per standard cubic meters",
            "current_date": "Report generation date and timestamp. Date format dd Mmm yyyy hh:mm:ss",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the daily heating value for each heating value zone for NSW/ACT networks (COUNTRY or NSWCR).\n\nAEMO processes files sent by distributors and publishes the heating values via this public MIBB report.\nThis process is only applicable to Network NSWCR and COUNTRY.\n\nThe 'Published Daily Zonal heating value for the day' is a CSV report listing all of the Heating\nValue zones where the distributor is the current distributor.\n\nThis report contains data for a period of 120 gas days (as available).\n",  # noqa: E501
        group_name=f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}",
    )

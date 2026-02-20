"""bronze_int871_v1_erftdailynslrpt_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int871_v1_erftdailynslrpt_1",
        s3_file_glob="int871_v1_erftdailynslrpt_1*",
        primary_keys=["network_id", "gas_date"],
        table_schema={
            "network_id": String,
            "gas_date": String,
            "gas_date_historical": String,
            "nsl_mj": Int64,
            "total_meter_count_basic": Int64,
            "normalisation_factor": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_id": "Network identifier",
            "gas_date": "Gas date being reported",
            "gas_date_historical": "Historical gas date",
            "nsl_mj": "Net section load in MJ",
            "total_meter_count_basic": "Total count of basic meters",
            "normalisation_factor": "Normalisation factor",
            "current_date": "Date and time report produced",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThe ERFTDailyNSLRpt report provides net section load and supporting data for each Network\nsection, in CSV format from AEMO to Retailers. The report is placed in the MIBB public folder\nas a .csv file.\n\nThis report is specific to NSW-ACT networks and provides information about the net section load,\ntotal meter count for basic meters, and normalisation factors for each network section.\n",  # noqa: E501
        group_name=f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}",
    )

"""bronze_int256_v4_mce_factor_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int256_v4_mce_factor_1",
        s3_file_glob="int256_v4_mce_factor_1*",
        primary_keys=["general_information_id"],
        table_schema={
            "general_information_id": Int64,
            "r_factor": Float64,
            "super_compressability_factor": Float64,
            "t_factor": Float64,
            "viscosity": Float64,
            "voll_price": Float64,
            "number_of_steps": Int64,
            "eod_linepack_min": Float64,
            "eod_linepack_max": Float64,
            "commencement_date": String,
            "termination_date": String,
            "last_mod_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "general_information_id": "General Information Identifier e.g. 5",
            "r_factor": "Ideal gas constant e.g. 47264",
            "super_compressability_factor": "Super Compressability Factor e.g. 859999999999999999",  # noqa: E501
            "t_factor": "Temperature of pipelines e.g. 288.0",
            "viscosity": "Viscosity e.g. 1.15e-005",
            "voll_price": "VOLL_Price ($/GJ) e.g. 800.0",
            "number_of_steps": "MCE Iterator e.g. 4",
            "eod_linepack_min": "End of Day Line Pack Minimum e.g. 0.0",
            "eod_linepack_max": "End of Day Line Pack Maximum e.g. 10000000000000001",
            "commencement_date": "e.g. 18 Jun 2001 16:34:57",
            "termination_date": "e.g. 19 Jun 2001 16:34:57",
            "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:34:57",
            "current_date": "Date and Time the report is produced e.g. 21 Jun 2001 16:34:57",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report lists what the standard parameters are that are used as input data for Market Clearing Engine (MCE) in generating\nschedules for the market.\n\nThis public report shows the current MCE factors and is produced when a change occurs to the factors.\n\nEach report contains the general information identifier.\n\nNote: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

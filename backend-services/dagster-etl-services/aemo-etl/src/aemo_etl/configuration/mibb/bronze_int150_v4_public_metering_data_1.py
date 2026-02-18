"""bronze_int150_v4_public_metering_data_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int150_v4_public_metering_data_1",
        s3_file_glob="int150_v4_public_metering_data_1*",
        primary_keys=["gas_date", "flag", "id", "ti"],
        table_schema={
            "gas_date": String,
            "flag": String,
            "id": String,
            "ti": Int64,
            "energy_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. as 30 Jun 1998",
            "flag": "WTHDL - int92 withdrawals, INJ - integer 98 injections",
            "id": "Meter registration number or withdrawal zone name",
            "ti": "Trading interval (1-24), where 1= 6:00 AM to 7:00 AM, 2= 7:00 AM to 8:00 AM, until the 24th interval",
            "energy_gj": "Energy value (GJ) (not adjusted for UAFG)",
            "current_date": "Time report produced",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis public report contains metering data grouped by withdrawal zone and injection point for the previous 2 months. This\nreport provides an industry overview of what is happening across the system (for example, quantity of energy flow and\ninjected). This report can be used by Participants to estimate their settlement exposure to the market. Participants should\nhowever be aware that the data is provisional and can change at settlement.\n\nParticipants should also be aware that this meter data is what is used by AEMO when prudential processing is done to assess\neach Market participants exposure to the market and the likelihood of a margin call being required.\n\nIt should be noted that this data is likely to have a proportion generated from substitutions and estimates and should only be\nused as a guide to the demand on that day.\n\nA report is produced three business days after the gas date.\nThis report can be accessed through the MIBB and AEMO websites.\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

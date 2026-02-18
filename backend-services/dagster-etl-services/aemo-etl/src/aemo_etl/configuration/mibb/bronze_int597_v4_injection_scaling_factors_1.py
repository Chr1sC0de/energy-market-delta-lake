"""bronze_int597_v4_injection_scaling_factors_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import QUEENSLAND_GAS_RETAIL_REPORT_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int597_v4_injection_scaling_factors_1",
        s3_file_glob="int597_v4_injection_scaling_factors_1*",
        primary_keys=[
            "network_name",
            "version_id",
            "gas_date",
            "distributor_name",
            "withdrawal_zone",
        ],
        table_schema={
            "network_name": String,
            "version_id": Int64,
            "gas_date": String,
            "distributor_name": String,
            "withdrawal_zone": String,
            "scaling_factor": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_name": "Network name",
            "version_id": "Null for provisional statement type",
            "gas_date": "Gas date being reported. Format dd mmm yyyy e.g. 01 Jul 2007",
            "distributor_name": "Distribution Business name",
            "withdrawal_zone": "Withdrawal zone",
            "scaling_factor": "Injection scaling factor",
            "current_date": "Date and Time report produced 15 Aug 2007 10:06:54",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is produced for the settlement period and shows the scaling factor adjustments for aggregated injections in\nDistribution region and withdrawal zone.\n\nThis public report shows the daily scaling factors used in adjusting the retailer injections to match the actual withdrawals in a\ndistribution region and withdrawal zone.\nThere is no equivalent VIC MIBB report.\n\nEach report contents the:\n- network name\n- statement version identifier\n- gas date\n- distributor name\n- withdrawal zone\n- scaling factor\n- current date\n",
        group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
    )

"""bronze_int261_v4_agg_amdq_transferred_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int261_v4_agg_amdq_transferred_1",
        s3_file_glob="int261_v4_agg_amdq_transferred_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "aggregated_amdq_transferred": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 02 Feb 2001",
            "aggregated_amdq_transferred": "Total AMDQ transffered each day for the previous month",
            "current_date": "Date and Time report produced e.g. 30 Jun 2007 06:00:00",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report displays the aggregated AMDQ transfer quantities for the previous 30 days. It registers the daily off market trades and\ntransfer amounts.\n\nA market participant report is produced on a monthly basis showing the total AMDQ transferred each day for the previous 30 days.\n\nEach report contains:\n- the gas date\n- the aggregated AMDQ transferred\n- the date and time when the report was produced\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

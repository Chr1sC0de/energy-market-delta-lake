"""bronze_int287_v4_gas_consumption_1 - Bronze MIBB report configuration."""

from polars import String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int287_v4_gas_consumption_1",
        s3_file_glob="int287_v4_gas_consumption_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "total_gas_used": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported (e.g. 30 Jun 2007)",
            "total_gas_used": "total gas used in gj",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis public report shows the daily gas consumed  at an operational level and \ntherefore will have minor discrepencies due ot metering substitutions or updates\npost the gas day\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

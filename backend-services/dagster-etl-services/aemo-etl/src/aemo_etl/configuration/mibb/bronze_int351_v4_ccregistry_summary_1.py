"""bronze_int351_v4_ccregistry_summary_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int351_v4_ccregistry_summary_1",
        s3_file_glob="int351_v4_ccregistry_summary_1*",
        primary_keys=["zone_id", "start_date", "end_date", "source"],
        table_schema={
            "zone_id": Int64,
            "zone_name": String,
            "zone_type": String,
            "start_date": String,
            "end_date": String,
            "total_holding_gj": Float64,
            "source": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "zone_type": "Type of CC zone. Entry/Exit",
            "start_date": "Starting CC product period start date. Dd mmm yyyy",
            "end_date": "Ending CC product period end date. Dd mmm yyyy",
            "total_holding_gj": "Total holding in GJ",
            "source": "Acquired source of the holding. Eg: AUCTION, DTSSP14",
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides a registry of the capacity certificates allocated to each auction product.\n\nThis report will provide the total capacity certificates that is allocated at each CC zone and period. The report aggregates the\nCC quantities won and paid for by all Market participants in a CC Auction for a CC zone and period. The report also provides\nquantities allocated by the DTS SP.\nThis report is published daily at midnight.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

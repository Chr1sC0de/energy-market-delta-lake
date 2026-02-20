"""bronze_int353_v4_ccauction_qty_won_all_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int353_v4_ccauction_qty_won_all_1",
        s3_file_glob="int353_v4_ccauction_qty_won_all_1*",
        primary_keys=["zone_id", "cc_period"],
        table_schema={
            "auction_id": Int64,
            "auction_date": String,
            "zone_id": Int64,
            "zone_name": String,
            "zone_type": String,
            "start_date": String,
            "end_date": String,
            "cc_period": String,
            "clearing_price": Float64,
            "quantities_won_gj": Float64,
            "unallocated_qty": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "auction_id": "Identifier number of the CC auction",
            "auction_date": "Auction run date. dd mmm yyyy",
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "zone_type": "Type of CC zone. Entry/Exit",
            "start_date": "Starting CC product period start date. Dd mmm yyyy",
            "end_date": "Ending CC product period end date. Dd mmm yyyy",
            "cc_period": "CC product period name representing date range period for the capacity",  # noqa: E501
            "clearing_price": "Price in which bid cleared",
            "quantities_won_gj": "Quantity won in GJ",
            "unallocated_qty": "Quantity not won in GJ",
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the CC capacities won at auction for the published CC auction by zone and period.\n\nA report is produced on approval of the CC auction results for a CC auction <ID>.\nThis report will show the CC auction results in csv format.\nAggregation of all quantities won by all Market participants.\nSort order is by Zone ID, calendar months for the years within auction period range.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

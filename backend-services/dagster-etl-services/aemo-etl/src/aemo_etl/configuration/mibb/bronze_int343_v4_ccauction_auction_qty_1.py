"""bronze_int343_v4_ccauction_auction_qty_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int343_v4_ccauction_auction_qty_1",
        s3_file_glob="int343_v4_ccauction_auction_qty_1*",
        primary_keys=["zone_id", "capacity_period"],
        table_schema={
            "auction_id": Int64,
            "zone_id": Int64,
            "zone_name": String,
            "zone_type": String,
            "capacity_period": String,
            "auction_date": String,
            "available_capacity_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "auction_id": "Identifier number of the CC auction",
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "zone_type": "Type of CC zone. Entry/Exit",
            "capacity_period": "Date ranged period the CC product applies to",
            "auction_date": "Auction run date. dd mmm yyyy",
            "available_capacity_gj": "Available capacity to bid on for opened auction in GJ",  # noqa: E501
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the CC capacities available for auction by zone and period after the announcement that the CC auction is\nopen.\n\nA report is produced when CC auction is triggered.\nThis report will show the auctionable quantity for each product for a particular auction ID in csv format.\nSort order is by Zone and Capacity Period in ascending order.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

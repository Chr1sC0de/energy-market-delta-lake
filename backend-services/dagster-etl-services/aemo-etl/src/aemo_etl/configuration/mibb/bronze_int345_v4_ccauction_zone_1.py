"""bronze_int345_v4_ccauction_zone_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int345_v4_ccauction_zone_1",
        s3_file_glob="int345_v4_ccauction_zone_1*",
        primary_keys=["zone_id"],
        table_schema={
            "zone_id": Int64,
            "zone_name": String,
            "zone_type": String,
            "from_date": String,
            "to_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "zone_type": "Type of CC zone. Entry/Exit",
            "from_date": "Effective from date of the zone",
            "to_date": "Effective end date of the zone",
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides a listing of the CC zones.\n\nThis report will be regenerated when CC zone data is updated.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

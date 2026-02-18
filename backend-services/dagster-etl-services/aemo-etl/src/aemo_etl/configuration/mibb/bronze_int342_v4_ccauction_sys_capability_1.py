"""bronze_int342_v4_ccauction_sys_capability_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int342_v4_ccauction_sys_capability_1",
        s3_file_glob="int342_v4_ccauction_sys_capability_1*",
        primary_keys=["zone_id", "capacity_period"],
        table_schema={
            "zone_id": Int64,
            "zone_name": String,
            "zone_type": String,
            "capacity_period": String,
            "zone_capacity_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "zone_type": "Type of CC zone. Entry/Exit",
            "capacity_period": "CC product period representing date range period for the capacity",
            "zone_capacity_gj": "Zone capacity as per current model in GJ",
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides the total CC zone modelled capacities by the auction period.\n\nThis report provides the total quantity of each auction product available for allocation on the basis of capacity certificates\nauction. The capacity certificates for a capacity certificates zone available for allocation will be the lower of either the\nmaximum pipeline capacity or maximum facility or system point/s deliverable capacity.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

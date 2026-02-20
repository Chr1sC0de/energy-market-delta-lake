"""bronze_int257_v4_linepack_with_zones_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int257_v4_linepack_with_zones_1",
        s3_file_glob="int257_v4_linepack_with_zones_1*",
        primary_keys=["linepack_zone_id"],
        table_schema={
            "linepack_zone_id": Int64,
            "linepack_zone_name": String,
            "last_mod_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "linepack_zone_id": "Linepack Zone in which the pipe segment exists e.g. 6",
            "linepack_zone_name": "Name of the linepack zone, e.g. Gippsland",
            "last_mod_date": "Time last modified e.g. 20 June 2001 16:39:58",
            "current_date": "Time the report is produced e.g. 21 Jun 2001 16:39:58",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains the current linepack zones.\n\nThis public report is produced when a change occurs.\n\nEach report contains the:\n- linepack zone where the pipe segment is located\n- linepack zone name\n- last modified date and time\n- date and time when the report was produced.\n\nNote: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

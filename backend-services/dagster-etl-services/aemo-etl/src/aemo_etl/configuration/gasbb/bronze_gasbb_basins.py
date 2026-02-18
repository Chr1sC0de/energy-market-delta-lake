"""bronze_gasbb_basins - Bronze GASBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_basins",
        s3_file_glob="gasbbbasins*",
        primary_keys=["BasinId"],
        table_schema={
            "BasinId": Int64,
            "BasinName": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "BasinId": "A unique AEMO defined Facility Identifier.",
            "BasinName": "The name of the basin. If short name exists then short name included in report.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="""

This report displays a list of all basins.

GASBB_BASINS is updated daily.

Contains all current basins.
""",
    )

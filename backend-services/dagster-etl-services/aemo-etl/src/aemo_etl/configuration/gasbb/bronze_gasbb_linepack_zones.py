"""bronze_gasbb_linepack_zones - Bronze GASBB report configuration."""

from polars import String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_linepack_zones",
        s3_file_glob="gasbblinepackzones*",
        primary_keys=["Operator", "LinepackZone"],
        table_schema={
            "Operator": String,
            "LinepackZone": String,
            "LinepackZoneDescription": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "Operator": "Operator of linepack zone",
            "LinepackZone": "Linepack Zone",
            "LinepackZoneDescription": "Description of Linepack Zone",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nDisplay list of operator to linepack zones with descriptions\n",  # noqa: E501
    )

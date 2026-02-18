"""bronze_gasbb_nt_lng_flow - Bronze GASBB report configuration."""

from polars import String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_nt_lng_flow",
        s3_file_glob="gasbbntlngflow*",
        primary_keys=["Gas Date", "Total Receipts", "Total Deliveries"],
        table_schema={
            "Gas Date": String,
            "Total Receipts": String,
            "Total Deliveries": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "Gas Date": "Gas Date",
            "Total Receipts": "Total Receipts",
            "Total Deliveries": "Total Deliveries",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nReport outlining lng total flows\n",
    )

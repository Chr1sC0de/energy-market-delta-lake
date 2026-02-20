"""bronze_int348_v4_cctransfer_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int348_v4_cctransfer_1",
        s3_file_glob="int348_v4_cctransfer_1*",
        primary_keys=["transfer_id", "zone_id", "start_date"],
        table_schema={
            "transfer_id": Int64,
            "zone_id": Int64,
            "zone_name": String,
            "start_date": String,
            "end_date": String,
            "transferred_qty_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "transfer_id": "Identifier number of the CC transfer",
            "zone_id": "Identifier number of CC zone",
            "zone_name": "Name of CC zone",
            "start_date": "Starting CC product period start date. Dd mmm yyyy",
            "end_date": "Ending CC product period end date. Dd mmm yyyy",
            "transferred_qty_gj": "CC amount in GJ transferred in the denoted transfer id",  # noqa: E501
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the approved CC transfer amounts conducted on the previous day.\n\nThis report will be published on the following gas day (D+1) if a transfer of capacity certificates has been approved on the\nprevious gas day. The report will be published at midnight. If no transfer of capacity certificates has been approved, the report\nwill not be published.\nThe report provides information about the amount of CC transferred for a CC zone and CC product period.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

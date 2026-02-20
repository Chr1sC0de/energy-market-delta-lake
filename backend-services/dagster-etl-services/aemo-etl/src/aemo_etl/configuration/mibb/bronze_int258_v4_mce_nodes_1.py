"""bronze_int258_v4_mce_nodes_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int258_v4_mce_nodes_1",
        s3_file_glob="int258_v4_mce_nodes_1*",
        primary_keys=["pipeline_id", "point_group_identifier_id"],
        table_schema={
            "pipeline_id": Int64,
            "point_group_identifier_id": Int64,
            "point_group_identifier_name": String,
            "nodal_altitude": Int64,
            "last_mod_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "pipeline_id": "Pipeline identifier e.g. 1",
            "point_group_identifier_id": "Point group identifier e.g. 4",
            "point_group_identifier_name": "Point group identifier name e.g. Rosebud",
            "nodal_altitude": "Nodal altitude e.g. 37",
            "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:42:35",
            "current_date": "Date and Time the report is produced e.g. 21 Jun 2001 16:42:35",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains the current MCE Nodes.\n\nThis public report is produced each time a change occurs.\nIt identifies nodes that the MCE uses. The nodal prices from MCE forms the network prices.\n\nEach report contains the:\n- pipeline identifier\n- point group identifier and name\n- nodal altitude\n- last modified date\n- date and time when the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

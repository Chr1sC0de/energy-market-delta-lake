"""bronze_int262_v4_spare_capacity_limits_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int262_v4_spare_capacity_limits_1",
        s3_file_glob="int262_v4_spare_capacity_limits_1*",
        primary_keys=["gas_date", "node_id"],
        table_schema={
            "gas_date": String,
            "node_id": Int64,
            "node_name": String,
            "current_system_capacity": Float64,
            "current_lateral_capacity": Float64,
            "max_system_capacity": Float64,
            "min_system_capacity": Float64,
            "max_lateral_capacity": Float64,
            "min_lateral_capacity": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas Date data generated e.g. 02 Feb 2001",
            "node_id": "AMDQ node ID",
            "node_name": "AMDQ node name",
            "current_system_capacity": "Current system spare capacity available for Gas Date (refer to Content notes)",
            "current_lateral_capacity": "Current lateral spare capacity available for Gas Date (refer to Content notes)",
            "max_system_capacity": "Maximum future system spare capacity available for Gas Date (refer to Content notes)",
            "min_system_capacity": "Minimum future system spare capacity available (refer to Content notes)",
            "max_lateral_capacity": "Maximum future lateral spare capacity available (refer to Content notes)",
            "min_lateral_capacity": "Minimum future lateral spare capacity available (refer to Content notes)",
            "current_date": "Date and Time report produced e.g. 21 May 2007 01:32:00",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report displays the current and future maximum and minimum 'lateral' and 'system' spare capacity available for each\nAMDQ node.\n\nThis report is generated daily for the current gas day.\n\nNull capacity values indicate the spare capacity is not calculated for this node as the spare capacity is considered very large.\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

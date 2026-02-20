"""bronze_gasbb_2p_sensitivities - Bronze GASBB report configuration."""

from polars import String, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_2p_sensitivities",
        s3_file_glob="gasbb2psensitivies*",
        primary_keys=["PeriodID", "State"],
        table_schema={
            "PeriodID": String,
            "State": String,
            "Increase": Float64,
            "Decrease": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "PeriodID": "relevant periods",
            "State": "state",
            "Increase": "increase value",
            "Decrease": "decrease value",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays information about Field Reserves and Resources.\n\nBoth GASBB_2P_SENSETIVITIES_ALL and GASBB_2P_SENSETIVITIES_LAST_QUARTER are updated monthly.\n\nContains all current reserve and resource information for a BB field interest.\n",  # noqa: E501
    )

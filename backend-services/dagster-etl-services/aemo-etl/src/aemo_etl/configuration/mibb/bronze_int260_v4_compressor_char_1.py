"""bronze_int260_v4_compressor_char_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int260_v4_compressor_char_1",
        s3_file_glob="int260_v4_compressor_char_1*",
        primary_keys=["compressor_id", "compressor_station_id"],
        table_schema={
            "compressor_id": Int64,
            "compressor_name": String,
            "pipe_segment_id": Int64,
            "min_pressure_delta": Float64,
            "most_efficient_pressure_delta": Float64,
            "max_pressure_delta": Float64,
            "max_compressor_power": Float64,
            "min_compressor_power": Float64,
            "compressor_efficiency": Float64,
            "compressor_efficiency_at_min": Float64,
            "efficiency_coefficient": Float64,
            "super_compressability_factor": Float64,
            "compressor_station_id": Int64,
            "station_name": String,
            "last_mod_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "compressor_id": "Compressor id e.g. 3",
            "compressor_name": "Compressor name e.g. Brooklyn Compressor No 4",
            "pipe_segment_id": "Pipe segment id e.g. 17",
            "min_pressure_delta": "Minimum pressure differential along segment e.g. 250.0",  # noqa: E501
            "most_efficient_pressure_delta": "Maximum efficiency at optimal pressure differential e.g. 960.0",  # noqa: E501
            "max_pressure_delta": "Max pressure differentials along a segment e.g. 1110.0",  # noqa: E501
            "max_compressor_power": "Max power available from each compressor e.g. 850.0",  # noqa: E501
            "min_compressor_power": "Min power available from each compressor e.g. 450.0",  # noqa: E501
            "compressor_efficiency": "Max efficiency of the compresorat its optimal pressure differential e.g. 68500000000000005",  # noqa: E501
            "compressor_efficiency_at_min": "Min efficiency at the least optimal pressure differential e.g. 330000000000000002",  # noqa: E501
            "efficiency_coefficient": "Coefficient for adjusting the efficiency of the compressor e.g. 1.5",  # noqa: E501
            "super_compressability_factor": "Super compressability of gas at compressor inlet e.g. 92000000000000004",  # noqa: E501
            "compressor_station_id": "Compressor station id e.g. 2",
            "station_name": "Station name e.g. Brooklyn Compressor Stage III",
            "last_mod_date": "Time last modified e.g. 10 Jun 2001 16:50:46",
            "current_date": "Time the report is produced e.g. 21 Jun2001 16:50:46",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains the current compressor characteristics, and this data is used as input to the MCE.\n\nThis public report is produced each time when a change occurs.\nEach report shows the minimum and maximum pressure change.\n\nEach report contains the:\n- compressor id and name\n- pipe segment id\n- pressure and compressor information\n- station name\n- last modified date\n\nNote: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

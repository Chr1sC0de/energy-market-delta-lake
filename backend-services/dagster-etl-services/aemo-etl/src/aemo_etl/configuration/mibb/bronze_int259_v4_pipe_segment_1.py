"""bronze_int259_v4_pipe_segment_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int259_v4_pipe_segment_1",
        s3_file_glob="int259_v4_pipe_segment_1*",
        primary_keys=["pipe_segment_id", "commencement_date"],
        table_schema={
            "pipe_segment_id": Int64,
            "pipe_segment_name": String,
            "linepack_zone_id": Int64,
            "commencement_date": String,
            "termination_date": String,
            "node_destination_id": Int64,
            "node_origin_id": Int64,
            "diameter": Float64,
            "diameter_paired": Float64,
            "length": Float64,
            "max_pressure": Float64,
            "min_pressure": Float64,
            "max_pressure_delta": Float64,
            "pressure_at_regulator_outlet": Float64,
            "regulator_at_origin": String,
            "reverse_flow": String,
            "compressor": String,
            "mean_pipe_altitude": Int64,
            "last_mod_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "pipe_segment_id": "Pipe segment id e.g. 1",
            "pipe_segment_name": "Pipe segment name e.g. Pre-Longford to Longford",
            "linepack_zone_id": "Linepack zone id e.g. 6",
            "commencement_date": "Commencement date e.g. 21 Jun 2001",
            "termination_date": "Termination date e.g. 21 Jun 2001",
            "node_destination_id": "Node destination id e.g. 3",
            "node_origin_id": "Last of the location node at the beginning of the segment e.g. 3",  # noqa: E501
            "diameter": "Last of diameter of pipe segment e.g. 74139999999999995",
            "diameter_paired": "Last of diameter of a parallel pipeline e.g. 741399999999995",  # noqa: E501
            "length": "Last of the length of pipe segment e.g. 64.79789999999998",
            "max_pressure": "Last of Max of available operating pressure e.g. 6850.0",
            "min_pressure": "Last of the operational minimum pressure e.g. 3500.0",
            "max_pressure_delta": "Last of max pressure differentials along a segment e.g. 1350.0",  # noqa: E501
            "pressure_at_regulator_outlet": "Pressure at regulator outlet e.g. 2760.0",
            "regulator_at_origin": "Yes denotes that a regulator exists e.g. N",
            "reverse_flow": "Yes denotes that the reverse flow os allowed e.g. Y",
            "compressor": "Yes denotes that the pipe segment has a compressor station on it e.g. N",  # noqa: E501
            "mean_pipe_altitude": "Mean pipe altitude e.g. 56",
            "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:44:46",
            "current_date": "Time the report is produced e.g. 21 Jun 2001 16:44:46",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains the current pipe segment definitions.\n\nThis public report is produced each time a change occurs.\nThe report is similar to INT258 and shows minimum and maximum volumes for pipelines and the pressure of gas.\n\nEach report contains the:\n- pipe segment id and name\n- linepack zone id\n- commencement and termination dates\n- node destination and origin id\n- pipe segment measurements\n- details of pressure\n- if a regulator, reverse flow and compressor exists\n- last modified date\n\nNote: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

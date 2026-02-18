"""bronze_int276_v4_hourly_scada_pressures_at_mce_nodes_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int276_v4_hourly_scada_pressures_at_mce_nodes_1",
        s3_file_glob="int276_v4_hourly_scada_pressures_at_mce_nodes_1*",
        primary_keys=["node_id", "measurement_datetime"],
        table_schema={
            "node_id": Int64,
            "node_name": String,
            "measurement_datetime": String,
            "current_hour": Float64,
            "hour_01_ago": Float64,
            "hour_02_ago": Float64,
            "hour_03_ago": Float64,
            "hour_04_ago": Float64,
            "hour_05_ago": Float64,
            "hour_06_ago": Float64,
            "hour_07_ago": Float64,
            "hour_08_ago": Float64,
            "hour_09_ago": Float64,
            "hour_10_ago": Float64,
            "hour_11_ago": Float64,
            "hour_12_ago": Float64,
            "hour_13_ago": Float64,
            "hour_14_ago": Float64,
            "hour_15_ago": Float64,
            "hour_16_ago": Float64,
            "hour_17_ago": Float64,
            "hour_18_ago": Float64,
            "hour_19_ago": Float64,
            "hour_20_ago": Float64,
            "hour_21_ago": Float64,
            "hour_22_ago": Float64,
            "hour_23_ago": Float64,
            "hour_24_ago": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "node_id": "MCE node ID",
            "node_name": "MCE node name",
            "measurement_datetime": "Date and Time of latest pressure measurement (e.g. 30 Jun 2011 12:00:00)",
            "current_hour": "pressure values at measurement time",
            "hour_01_ago": "pressure values for 1 hour before measurement time",
            "hour_02_ago": "pressure values for 2 hours before measurement time",
            "hour_03_ago": "pressure values for 3 hours before measurement time",
            "hour_04_ago": "pressure values for 4 hours before measurement time",
            "hour_05_ago": "pressure values for 5 hours before measurement time",
            "hour_06_ago": "pressure values for 6 hours before measurement time",
            "hour_07_ago": "pressure values for 7 hours before measurement time",
            "hour_08_ago": "pressure values for 8 hours before measurement time",
            "hour_09_ago": "pressure values for 9 hours before measurement time",
            "hour_10_ago": "pressure values for 10 hours before measurement time",
            "hour_11_ago": "pressure values for 11 hours before measurement time",
            "hour_12_ago": "pressure values for 12 hours before measurement time",
            "hour_13_ago": "pressure values for 13 hours before measurement time",
            "hour_14_ago": "pressure values for 14 hours before measurement time",
            "hour_15_ago": "pressure values for 15 hours before measurement time",
            "hour_16_ago": "pressure values for 16 hours before measurement time",
            "hour_17_ago": "pressure values for 17 hours before measurement time",
            "hour_18_ago": "pressure values for 18 hours before measurement time",
            "hour_19_ago": "pressure values for 19 hours before measurement time",
            "hour_20_ago": "pressure values for 20 hours before measurement time",
            "hour_21_ago": "pressure values for 21 hours before measurement time",
            "hour_22_ago": "pressure values for 22 hours before measurement time",
            "hour_23_ago": "pressure values for 23 hours before measurement time",
            "hour_24_ago": "pressure values for 24 hours before measurement time",
            "current_date": "Date and Time report created (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis public report is to provide 25 hours of rolling hourly SCADA pressures corresponding to MCE Node (i.e. pressure values\nfor the current and the preceding 24 hours).\n\nThe report contains real time data for actual SCADA pressure reading values in kPa corresponding to MCE nodes post\nvalidation. As these pressure values are subject to validation and substitution methodology, there may be substituted pressure\nreadings.\n\nCurrent and previous 24 hours values from the measurement time are displayed.\nWhere no value is present for a given hour, a NULL will be shown.\nMCE Nodes are set out in INT258 – MCE Nodes.\nHourly pressure values are in kPa units.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )

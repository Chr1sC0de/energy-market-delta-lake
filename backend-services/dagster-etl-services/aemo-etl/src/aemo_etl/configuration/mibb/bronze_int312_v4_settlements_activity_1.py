"""bronze_int312_v4_settlements_activity_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int312_v4_settlements_activity_1",
        s3_file_glob="int312_v4_settlements_activity_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "uafg_28_days_pct": Float64,
            "total_scheduled_inj_gj": Float64,
            "total_scheduled_wdl_gj": Float64,
            "total_actual_inj_gj": Float64,
            "total_actual_wdl_gj": Float64,
            "total_uplift_amt": Float64,
            "su_uplift_amt": Float64,
            "cu_uplift_amt": Float64,
            "vu_uplift_amt": Float64,
            "tu_uplift_amt": Float64,
            "ru_uplift_amt": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "dd mmm yyyy",
            "uafg_28_days_pct": "Uafg-28-day-rolling in pct",
            "total_scheduled_inj_gj": "Total scheduled injection in GJ",
            "total_scheduled_wdl_gj": "Sum of total scheduled controllable withdrawals, demand forecasts and AEMO's over-ride in GJ",
            "total_actual_inj_gj": "Total actual injection in GJ",
            "total_actual_wdl_gj": "Total actual withdrawals in GJ",
            "total_uplift_amt": "Total uplift in $",
            "su_uplift_amt": "Total surprise uplift in $",
            "cu_uplift_amt": "Total congestion uplift in $",
            "vu_uplift_amt": "Total common uplift resulting from unallocated AEMO's demand forecast over-ride in $",
            "tu_uplift_amt": "Total common uplift from exceedance of DTSP's liability limit in $",
            "ru_uplift_amt": "Total residual commin uplift in $",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose='\n\nThis report is to provide the market with information about settlement activity for the previous 12 months. Participants may\nwish to use this report to monitor market activity in the industry.\n\nA report is produced daily to the public with a rolling 12-month period.\n"uafg" in the second column of the report refers to unaccounted for gas shown in percentage. This could be due to a number of\nreasons, such as measurement errors or leakages. This report will show the "uatg" for a rolling 28-day period.\n',
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

"""bronze_int291_v4_out_of_merit_order_gas_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int291_v4_out_of_merit_order_gas_1",
        s3_file_glob="int291_v4_out_of_merit_order_gas_1*",
        primary_keys=["gas_date", "statement_version_id"],
        table_schema={
            "gas_date": String,
            "statement_version_id": Int64,
            "ancillary_amt_gst_ex": Float64,
            "scheduled_out_of_merit_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day dd mmm yyy e.g.30 Jun 2008",
            "statement_version_id": "Statement version ID",
            "ancillary_amt_gst_ex": "Total estimated AP for the gas day (net position as at the last schedule of the day) ancillary_amt_gst_ex = SUM(payment_amt) FROM ap_daily_sched_mirn per gas_date for inj_wdl_flag = 'I'",
            "scheduled_out_of_merit_gj": "Net out of merit order GJs scheduled and delivered over the day scheduled_out_of merit_gj = SUM(ap_qty_gj) FROM ap_constrained_up per gas_date for inj_wdl_flag = 'I'",
            "current_date": "Current report run date time. Format dd Mmm yyyy hh:mi:ss e.g. 15 May 2008 12:22:12",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis is a public report generated for actual volumes of gas that contribute to APs (volumes of out of merit order gas). Report to\nbe on the issue of each settlement (M+7, M+18 and M+118).\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

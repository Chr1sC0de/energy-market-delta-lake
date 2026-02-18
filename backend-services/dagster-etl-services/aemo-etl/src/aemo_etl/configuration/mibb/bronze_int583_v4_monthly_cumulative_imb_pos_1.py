"""bronze_int583_v4_monthly_cumulative_imb_pos_1 - Bronze MIBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration import QUEENSLAND_GAS_RETAIL_REPORT_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int583_v4_monthly_cumulative_imb_pos_1",
        s3_file_glob="int583_v4_monthly_cumulative_imb_pos_1*",
        primary_keys=[
            "network_name",
            "version_id",
            "fro_name",
            "distributor_name",
            "withdrawal_zone",
        ],
        table_schema={
            "network_name": String,
            "version_id": Int64,
            "fro_name": String,
            "distributor_name": String,
            "withdrawal_zone": String,
            "curr_cum_date": String,
            "curr_cum_imb_position": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_name": "Network Name",
            "version_id": "Settlement statement version identifier",
            "fro_name": "Name of Financially Responsible Organisation",
            "distributor_name": "Distribution business name",
            "withdrawal_zone": "Withdrawal zone",
            "curr_cum_date": "Current cumulative imbalance issue date",
            "curr_cum_imb_position": "Surplus or Deficit or Balance",
            "current_date": "Date and Time report produced 15 Aug 2007 10:06:54",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report shows the cumulative imbalance position of Retailers. Retailers may wish to use this report to track their status of\nthe imbalance to do the necessary adjustments.\n\nThis public report is updated at each issue of settlement to show the status of each retailer's imbalance position.\nThere is no equivalent VIC MIBB report.\n\nEach report contains the:\n- network name\n- statement version id\n- financially Responsible Organisation\n- distributor Name\n- withdrawal zone\n- current cumulative imbalance issue date\n- current cumulative imbalance position (Surplus, Deficit or Balanced)\n- date and time report produced\n",
        group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
    )

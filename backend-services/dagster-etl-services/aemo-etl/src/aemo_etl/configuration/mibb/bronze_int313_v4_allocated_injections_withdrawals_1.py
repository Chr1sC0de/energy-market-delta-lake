"""bronze_int313_v4_allocated_injections_withdrawals_1 - Bronze MIBB report configuration."""  # noqa: E501

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int313_v4_allocated_injections_withdrawals_1",
        s3_file_glob="int313_v4_allocated_injections_withdrawals_1*",
        primary_keys=["gas_date", "gas_hour", "phy_mirn"],
        table_schema={
            "gas_date": String,
            "gas_hour": String,
            "site_company": String,
            "phy_mirn": String,
            "inject_withdraw": String,
            "energy_flow_gj": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "dd mmm yyyy",
            "gas_hour": """
                The start time of the gas day 9:00:00 pre GMP and 6:00:00 post GMP start
            """,
            "site_company": "Site Company Name",
            "phy_mirn": "Phy_mirn (commissioned = 'Y', biddin = 'Y')",
            "inject_withdraw": "Sum of Actual Injections",
            "energy_flow_gj": "Actual GJ",
            "surrogate_key": """
                Unique identifier created using sha256 over the primary keys
            """,
        },
        report_purpose="""
            This is a public report that provides historical injection and controllable
            withdrawal information in a form that has been structured to facilitate
            graphing and trend analysis of the energy flows in the gas network: - out of
            the network at transmission withdrawal points - into the network at
            transmission injection points.

            This report does not contain a current date column to assist in graphing
            data directly from presented figures. The energy withdrawals reported in
            INT313 are controllable withdrawals.

            Each report contains daily data for the last 12 months. For each gas day
            date reported, a separate row will list the energy flow (in GJ) associated
            with each transmission pipeline injection or withdrawal MIRN.
        """,
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

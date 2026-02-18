"""bronze_gasbb_short_term_transactions - Bronze GASBB report configuration."""

from polars import String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_short_term_transactions",
        s3_file_glob="gasbbshorttermtransactions*",
        primary_keys=[
            "PeriodID",
            "State",
            "TransactionType",
            "SupplyPeriodStart",
            "SupplyPeriodEnd",
        ],
        table_schema={
            "PeriodID": String,
            "State": String,
            "Quantity (TJ)": String,
            "VolumeWeightedPrice ($)": String,
            "TransactionType": String,
            "SupplyPeriodStart": String,
            "SupplyPeriodEnd": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "PeriodID": "Swap period",
            "State": "state for the swap",
            "Quantity (TJ)": "quantity",
            "VolumeWeightedPrice ($)": "volume weighted price",
            "TransactionType": "swap transaction type",
            "SupplyPeriodStart": "supply period start of swap",
            "SupplyPeriodEnd": "supply period endo of swap",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThese reports display short term gas transactions for each state/territory, excluding those transactions that are concluded through an AEMO operated exchange. Reports for VIC and QLD are updated weekly while others are updated monthly.\n",
    )

"""bronze_gasbb_lng_transactions - Bronze GASBB report configuration."""

from polars import String, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_lng_transactions",
        s3_file_glob="gasbblngtransactions*",
        primary_keys=["TransactionMonth", "SupplyStartDate", "SupplyEndDate"],
        table_schema={
            "TransactionMonth": String,
            "VolWeightPrice": Float64,
            "Volume": Float64,
            "SupplyStartDate": String,
            "SupplyEndDate": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "TransactionMonth": "Transaction month.",
            "VolWeightPrice": "The volume weighted price for the reporting period.",
            "Volume": "The total volume of the transactions for the reporting period.",
            "SupplyStartDate": "The earliest start date of all transactions captured in the reporting period.",  # noqa: E501
            "SupplyEndDate": "The latest end date of all transactions captured in the reporting period.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays an LNG transaction aggregated data.\n\nGASBB_LNG_TRANSACTIONS is updated monthly.\n\nContains all short term LNG Export transactions.\n",  # noqa: E501
    )

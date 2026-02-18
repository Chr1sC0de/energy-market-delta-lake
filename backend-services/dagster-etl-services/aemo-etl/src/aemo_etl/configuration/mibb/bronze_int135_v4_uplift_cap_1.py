"""bronze_int135_v4_uplift_cap_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int135_v4_uplift_cap_1",
        s3_file_glob="int135_v4_uplift_cap_1*",
        primary_keys=["gas_date", "schedule_no"],
        table_schema={
            "gas_date": String,
            "schedule_no": Int64,
            "positive_ave_ancillary_rate": Float64,
            "negative_ave_ancillary_rate": Float64,
            "positive_uplift_rate": Float64,
            "negative_uplift_rate": Float64,
            "current_datetime": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day Format: dd mm yyyy e.g. 23 Jul 2008",
            "schedule_no": "Pricing schedule horizon that the uplift payment applies to",
            "positive_ave_ancillary_rate": "Positive average ancillary rate over all injection and withdrawal points and all MP's. PAVAPR variable from the ancillary payment calculations.",
            "negative_ave_ancillary_rate": "Negative average ancillary rate over all injection and withdrawal points and all MP's. NAVAPR variable from the ancillary payment calculations.",
            "positive_uplift_rate": "Positive uplift rate. UPR(P) variable from the uplift payment calculation.",
            "negative_uplift_rate": "Negative uplift rate. UPR(N) variable from the uplift payment calculation.",
            "current_datetime": "When report produced. The format is dd mm yyyy hh:mm:ss e.g. 23 Jul 2008 16:30:35",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nTo provide aggregated information used in Ancillary and Uplift payments calculations.\n\nThis public report is produced whenever ancillary and uplift payments are required.\n\nThe variables PAVAPR and NAVAPR are the average rate of ancillary payment as described in the Ancillary Payment\nProcedures.\n\nThe variables UPR(P) and UPR(N) are part of the uplift rate cap as described in the Uplift Payment Procedures.\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )

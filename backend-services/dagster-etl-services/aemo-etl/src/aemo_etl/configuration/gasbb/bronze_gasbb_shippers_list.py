"""bronze_gasbb_shippers_list - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_shippers_list",
        s3_file_glob="gasbbshippers*",
        primary_keys=["EffectiveDate", "FacilityId", "ShipperName", "LastUpdated"],
        table_schema={
            "EffectiveDate": String,
            "FacilityId": Int64,
            "FacilityName": String,
            "FacilityType": String,
            "CompanyId": Int64,
            "OperatorName": String,
            "ShipperName": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "EffectiveDate": "Gas date that corresponding record takes effect.",
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "FacilityName": "The name of the BB facility.",
            "FacilityType": "The type of facility.",
            "CompanyId": "Unique identifier for the company who operates the facility.",
            "OperatorName": "The name of the company who operates the facility.",
            "ShipperName": "The name of the shipper who holds the capacity.",
            "LastUpdated": "The date data was last submitted.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nA list shippers who have contracted primary Storage, Compression or Pipeline capacity.\n\nThis report is updated daily.\n\nGASBB_SHIPPERS_LIST contains current records / GASBB_SHIPPERS_FULL_LIST includes historic records.\n",  # noqa: E501
    )

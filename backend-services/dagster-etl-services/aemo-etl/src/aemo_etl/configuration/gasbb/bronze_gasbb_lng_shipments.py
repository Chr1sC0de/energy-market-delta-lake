"""bronze_gasbb_lng_shipments - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_lng_shipments",
        s3_file_glob="gasbblngshipments*",
        primary_keys=["TransactionId", "FacilityId", "VersionDateTime"],
        table_schema={
            "TransactionId": String,
            "FacilityId": Int64,
            "FacilityName": String,
            "VolumePJ": Float64,
            "ShipmentDate": String,
            "VersionDateTime": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "TransactionId": "Unique shipment identifier.",
            "FacilityId": "Unique facility identifier.",
            "FacilityName": "Name of the facility.",
            "VolumePJ": "Volume of the shipment in PJ.",
            "ShipmentDate": "For LNG export facility, the departure date. For LNG import facility, the date unloading commences at the LNG import facility.",  # noqa: E501
            "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report displays a list of all LNG shipments.\n\nGASBB_LNG_EXPO_IMPO_SHIPMENTS is updated monthly.\n",  # noqa: E501
    )

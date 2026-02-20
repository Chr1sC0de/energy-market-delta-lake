"""bronze_gasbb_actual_flow_storage - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_actual_flow_storage",
        s3_file_glob="gasbbactualflowstorage*",
        primary_keys=["GasDate", "FacilityId", "LocationId", "LastUpdated"],
        table_schema={
            "GasDate": String,
            "FacilityName": String,
            "State": String,
            "LocationId": Int64,
            "LocationName": String,
            "Demand": Float64,
            "Supply": Float64,
            "TransferIn": Float64,
            "TransferOut": Float64,
            "HeldInStorage": Float64,
            "FacilityId": Int64,
            "FacilityType": String,
            "CushionGasStorage": Float64,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityName": "Name of the facility.",
            "State": "Name of the state.",
            "LocationId": "Unique location identifier.",
            "LocationName": "Name of the location.",
            "Demand": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "Supply": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "TransferIn": "Usage type. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "TransferOut": "Usage type. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "HeldinStorage": "Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "FacilityType": "The type of facility (e.g., BBGPG, COMPRESSOR, PIPE, PROD, STOR, LNGEXPORT, LNGIMPORT, BBLARGE).",  # noqa: E501
            "CushionGasStorage": "The quantity of gas that must be retained in the Storage or LNG Import facility in order to maintain the required pressure and deliverability rates.",  # noqa: E501
            "LastUpdated": "The date data was last submitted by a participant based on the report query.",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThe report shows Daily Production, Flow and Storage data aggregated by Facility Id for an outlook period.\n\nThis report is updated daily and shows historic records back to Sep 2018.\nThere is also a GASBB_ACTUAL_FLOW_STORAGE_LAST_31 variant that is updated within 30 minutes of receiving new data and shows records from the last 31 days.\n\nThe report can be filtered by:\n- State\n- Facility Type\n- Facilities\n",  # noqa: E501
    )

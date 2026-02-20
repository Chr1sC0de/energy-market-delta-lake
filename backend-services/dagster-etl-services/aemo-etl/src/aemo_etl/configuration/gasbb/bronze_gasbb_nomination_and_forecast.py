"""bronze_gasbb_nomination_and_forecast - Bronze GASBB report configuration."""

from polars import String, Int64, Float64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_nomination_and_forecast",
        s3_file_glob="gasbbnominationandforecast*",
        primary_keys=["Gasdate", "FacilityId", "LocationId", "LastUpdated"],
        table_schema={
            "Gasdate": String,
            "FacilityName": String,
            "FacilityType": String,
            "State": String,
            "LocationName": String,
            "Demand": Float64,
            "Supply": Float64,
            "TransferIn": Float64,
            "TransferOut": Float64,
            "FacilityId": Int64,
            "LocationId": Int64,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day.",
            "FacilityName": "The name of the BB facility.",
            "FacilityType": "Facility type associated with the Facility Id.",
            "State": "Name of the state.",
            "LocationName": "Name of the location.",
            "Demand": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "Supply": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "TransferIn": "Usage type expressed in TJ. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "TransferOut": "Usage type expressed in TJ. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",  # noqa: E501
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "LocationId": "Unique location identifier.",
            "LastUpdated": "Date file was last updated.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThe report shall return Nomination and Forecast data submitted to the market.\nNomination and Forecasts data shall be aggregated by BB facility.\n\nGASBB_NOMINATION_AND_FORECAST is updated daily.\nGASBB_NOMINATION_AND_FORECAST_NEXT_7 is typically updated within 30 minutes of receiving new data.\n\nGASBB_NOMINATION_AND_FORECAST report contain historical data as well as nominations for D+0, D+1, D+2, D+3, D+4, D+5, and D+6. \nGASBB_NOMINATION_AND_FORECAST_NEXT_7 report covers the outlook period of D+0, D+1, D+2, D+3, D+4, D+5, and D+6.\n",  # noqa: E501
    )

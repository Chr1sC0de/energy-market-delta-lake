from logging import Logger
from datetime import timedelta

from polars import LazyFrame, col, lit
from aemo_etl.configuration.gasbb.bronze_gasbb_forecast_utilisation import (
    group_name,
    primary_keys,
    report_purpose,
    s3_file_glob,
    s3_prefix,
    s3_table_location,
    schema_descriptions,
    table_name,
    table_schema,
    upsert_predicate,
)
from aemo_etl.definitions.bronze_gasbb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list


core_columns = [
    "State",
    "FacilityId",
    "FacilityName",
    "FacilityType",
    "ReceiptLocationId",
    "ReceiptLocationName",
    "DeliveryLocationId",
    "DeliveryLocationName",
    "Description",
    "ForecastMethod",
    "Units",
    "Nameplate",
    "source_file",
]


def preprocess_hook(logger: Logger | None, df: LazyFrame) -> LazyFrame:
    if logger is not None:
        logger.info("upivoting data and adding new columns")
    all_columns = df.collect_schema().keys()
    forecast_columns = [
        col for col in all_columns if col not in core_columns and col != "source_file"
    ]
    forecast_column_mapping = {c: f"d+{i + 1}" for i, c in enumerate(forecast_columns)}
    df_unpivoted = df.unpivot(
        index=core_columns, variable_name="ForecastDate", value_name="ForecastValue"
    ).with_columns(ForecastDay=col.ForecastDate.replace(forecast_column_mapping))
    forecast_period = (
        df_unpivoted.select("ForecastDate")
        .unique()
        .with_columns(col("ForecastDate").str.to_datetime(format="%A %d %b %Y"))
        .collect()
        .min()
        .item()
        - timedelta(days=1)
    ).strftime("%A %d %b %Y")
    if logger is not None:
        logger.info("finished upivoting data and adding new columns")
    return df_unpivoted.select(
        "State",
        "FacilityId",
        "FacilityName",
        "FacilityType",
        "ReceiptLocationId",
        "ReceiptLocationName",
        "DeliveryLocationId",
        "DeliveryLocationName",
        "Description",
        "ForecastMethod",
        lit(forecast_period).alias("ForecastedFrom"),
        "ForecastDate",
        "ForecastDay",
        "Units",
        "ForecastValue",
        "Nameplate",
        "source_file",
    ).sort(primary_keys)


definition_builder = definition_builder_factory(
    report_purpose,
    table_schema,
    schema_descriptions,
    primary_keys,
    upsert_predicate,
    s3_table_location,
    s3_prefix,
    s3_file_glob,
    table_name,
    group_name=group_name,
    preprocess_hook=preprocess_hook,
    cpu="1024",
    memory="8192",
)

definitions_list.append(definition_builder.build())

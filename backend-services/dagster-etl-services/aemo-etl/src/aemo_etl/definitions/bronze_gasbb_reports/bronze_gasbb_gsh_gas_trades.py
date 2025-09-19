from logging import Logger

from dagster import AssetExecutionContext
from polars import LazyFrame, lit, read_csv

from aemo_etl.configuration.gasbb.bronze_gasbb_gsh_gas_trades import (
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
    default_post_process_hook,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list


def process_object_hook(_: Logger | None, contents: bytes) -> LazyFrame:
    csv_string = "\n".join(
        [
            ",".join(line.split(",")[4:])
            for line in contents.decode("utf-8").replace("\r\n", "\n").split("\n")[1:-2]
        ]
    ).encode()
    return read_csv(csv_string).lazy()


def custom_postprocess_hook(
    context: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: list[str],
    datetime_pattern: str | None = None,
    datetime_column_name: str | None = None,
) -> LazyFrame:
    context.log.info("ensuring rows are not duplicates")
    schema = df.collect_schema()

    for key in primary_keys:
        if key not in schema:
            df = df.with_columns(lit(None).alias(key))

    # filter out already existing columns

    df = default_post_process_hook(
        context,
        df,
        primary_keys=primary_keys,
        datetime_pattern=datetime_pattern,
        datetime_column_name=datetime_column_name,
    )

    return df


definition_builder = definition_builder_factory(
    report_purpose=report_purpose,
    table_schema=table_schema,
    schema_descriptions=schema_descriptions,
    primary_keys=primary_keys,
    upsert_predicate=upsert_predicate,
    s3_table_location=s3_table_location,
    s3_prefix=s3_prefix,
    s3_file_glob=s3_file_glob,
    table_name=table_name,
    group_name=group_name,
    process_object_hook=process_object_hook,
    post_process_hook=custom_postprocess_hook,
)

definitions_list.append(definition_builder.build())

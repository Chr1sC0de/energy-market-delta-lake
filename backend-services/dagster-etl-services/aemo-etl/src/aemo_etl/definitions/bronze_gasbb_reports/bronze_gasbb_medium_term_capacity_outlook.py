from dagster import AssetExecutionContext
from polars import LazyFrame, col, scan_delta
from polars import len as len_

from aemo_etl.configuration.gasbb.bronze_gasbb_medium_term_capacity_outlook import (
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

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │      create a custom post process hook which removes columns which are duplicates      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def medium_term_capacity_post_process_hook(
    context: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: list[str],
    datetime_pattern: str | None = None,
    datetime_column_name: str | None = None,
) -> LazyFrame:
    context.log.info("ensuring rows are not duplicates")
    df = default_post_process_hook(
        context,
        df,
        primary_keys=primary_keys,
        datetime_pattern=datetime_pattern,
        datetime_column_name=datetime_column_name,
    )
    try:
        context.log.info("ensuring rows don't already exist based off primary keys")
        target_df = scan_delta(s3_table_location)

        context.log.info(
            f"initial rows for processed data = {df.select(len_()).collect().item()}"
        )
        type_matched_df = df.with_columns(
            col(col_).cast(type_)
            for col_, type_ in target_df.collect_schema().items()
            if col_ in df.collect_schema()
        )
        output = type_matched_df.join(
            scan_delta(s3_table_location),
            how="anti",
            on=primary_keys,
            nulls_equal=True,
        ).lazy()
        context.log.info(
            f"final rows for processed data = {output.select(len_()).collect().item()}"
        )
        return output
    except Exception as e:
        context.log.info(
            f"unable to complete post-process for rows with error message {e}"
        )
        return df


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
)

definitions_list.append(definition_builder.build())

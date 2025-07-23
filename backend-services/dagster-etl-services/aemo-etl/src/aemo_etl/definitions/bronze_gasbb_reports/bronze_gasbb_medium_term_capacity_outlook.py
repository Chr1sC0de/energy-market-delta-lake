from dagster import AssetExecutionContext
from polars import LazyFrame, scan_delta

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
    datetime_pattern: str | None = "%Y/%m/%d %H:%M:%S",
) -> LazyFrame:
    context.log.info("ensuring rows are not duplicates")
    df = default_post_process_hook(
        context, df, primary_keys=primary_keys, datetime_pattern=datetime_pattern
    )
    try:
        output = (
            df.join(
                scan_delta(s3_table_location),
                how="anti",
                on=primary_keys,
                nulls_equal=True,
            )
            .collect()
            .lazy()
        )

        return output
    except Exception:
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
    post_process_hook=medium_term_capacity_post_process_hook,
    datetime_pattern="%Y/%m/%d %H:%M:%S",
)

definitions_list.append(definition_builder.build())

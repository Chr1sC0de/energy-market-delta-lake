from logging import Logger

from polars import LazyFrame

from aemo_etl.configuration.gasbb.bronze_gasbb_nameplate_rating import (
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


def preprocess_hook(logger: Logger | None, df: LazyFrame) -> LazyFrame:
    if logger is not None:
        logger.info("making all columns lowercase")
    columns = df.collect_schema().keys()
    return df.rename({c: c.lower() for c in columns})


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
)

definitions_list.append(definition_builder.build())


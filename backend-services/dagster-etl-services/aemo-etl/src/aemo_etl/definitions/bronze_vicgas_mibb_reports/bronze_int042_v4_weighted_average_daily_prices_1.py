from aemo_etl.configuration.mibb.bronze_int042_v4_weighted_average_daily_prices_1 import (
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
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list

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
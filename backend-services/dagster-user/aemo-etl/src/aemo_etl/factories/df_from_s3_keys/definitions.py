from collections.abc import Mapping
from typing import Iterable

from dagster import (
    AssetIn,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Definitions,
)
from dagster._core.definitions.assets.definition.asset_dep import CoercibleToAssetDep
from polars import LazyFrame
from polars._typing import PolarsDataType

from aemo_etl.configs import AEMO_BUCKET, DEFAULT_SENSOR_STATUS
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.factories.df_from_s3_keys.assets import (
    bronze_df_from_s3_keys_asset_factory,
    silver_df_from_s3_keys_asset_factory,
)
from aemo_etl.factories.df_from_s3_keys.hooks import Hook
from aemo_etl.utils import get_metadata_schema


def df_from_s3_keys_definitions_factory(
    domain: str,
    name_suffix: str,
    glob_pattern: str,
    schema: Mapping[str, PolarsDataType],
    schema_descriptions: Mapping[str, str],
    surrogate_key_sources: list[str],
    bronze_postprocess_object_hooks: list[Hook[bytes]] | None = None,
    bronze_postprocess_lazyframe_hooks: list[Hook[LazyFrame]] | None = None,
    group_name: str | None = None,
    deps: Iterable[CoercibleToAssetDep] | None = None,
    description: str | None = None,
    bronze_op_tags: Mapping[str, object] | None = None,
    silver_op_tags: Mapping[str, object] | None = None,
) -> Definitions:

    bronze_key_prefix = ["bronze", domain]
    bronze_table_name = f"bronze_{name_suffix}"
    bronze_uri = f"s3://{AEMO_BUCKET}/{'/'.join(bronze_key_prefix)}/{bronze_table_name}"

    bronze_asset = bronze_df_from_s3_keys_asset_factory(
        uri=bronze_uri,
        schema=schema,
        surrogate_key_sources=surrogate_key_sources,
        postprocess_object_hooks=bronze_postprocess_object_hooks,
        postprocess_lazyframe_hooks=bronze_postprocess_lazyframe_hooks,
        key_prefix=bronze_key_prefix,
        name=bronze_table_name,
        group_name=group_name,
        io_manager_key="aemo_deltalake_ingest_partitioned_append_io_manager",
        deps=deps,
        description=f"Bronze dataset, contains full un-cleansed dataset.\n\n{description}",
        op_tags=bronze_op_tags or {},
        metadata={
            "dagster/column_schema": get_metadata_schema(schema, schema_descriptions),
            "surrogate_key_sources": surrogate_key_sources,
            "dagster/table_name": f"aemo.{domain}.{bronze_table_name}",
            "dagster/uri": bronze_uri,
            "glob_pattern": glob_pattern,
        },
    )

    bronze_asset_schema_check = schema_matches_check_factor(
        schema=schema,
        assets_definition=bronze_asset,
        check_name="check_schema_matches",
        description="Check observed schema matches target schema",
    )
    bronze_asset_schema_drift_check = schema_drift_check_factory(
        schema=schema,
        assets_definition=bronze_asset,
        check_name="check_schema_drift",
        description="Check for schema drift against the declared asset schema",
    )

    silver_key_prefix = ["silver", domain]
    silver_table_name = f"silver_{name_suffix}"
    silver_uri = f"s3://{AEMO_BUCKET}/{'/'.join(silver_key_prefix)}/{silver_table_name}"

    silver_asset = silver_df_from_s3_keys_asset_factory(
        key_prefix=silver_key_prefix,
        name=silver_table_name,
        group_name=f"{group_name}_cleansed",
        io_manager_key="aemo_parquet_overwrite_io_manager",
        ins={"df": AssetIn(bronze_asset.key)},
        description=f"Silver dataset, contains source-file deduplicated current rows.\n\n{description}",
        op_tags=silver_op_tags or {},
        metadata={
            "dagster/column_schema": get_metadata_schema(schema, schema_descriptions),
            "surrogate_key_sources": surrogate_key_sources,
            "dagster/table_name": f"silver.{domain}.{silver_table_name}",
            "dagster/uri": silver_uri,
            "bronze_table_name": f"aemo.{domain}.{bronze_table_name}",
            "glob_pattern": glob_pattern,
        },
        automation_condition=AutomationCondition.any_deps_updated()
        & ~AutomationCondition.in_progress(),
    )

    silver_asset_duplicate_row_check = duplicate_row_check_factory(
        assets_definition=silver_asset,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description=f"Check that surrogate_key({surrogate_key_sources}) is unique",
    )

    silver_asset_schema_check = schema_matches_check_factor(
        schema=schema,
        assets_definition=silver_asset,
        check_name="check_schema_matches",
        description="Check observed schema matches target schema",
    )

    silver_asset_schema_drift_check = schema_drift_check_factory(
        schema=schema,
        assets_definition=silver_asset,
        check_name="check_schema_drift",
        description="Check for schema drift against the declared asset schema",
    )

    return Definitions(
        assets=[bronze_asset, silver_asset],
        asset_checks=[
            bronze_asset_schema_check,
            bronze_asset_schema_drift_check,
            silver_asset_duplicate_row_check,
            silver_asset_schema_check,
            silver_asset_schema_drift_check,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name=f"{silver_table_name}_sensor",
                target=[silver_asset.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )

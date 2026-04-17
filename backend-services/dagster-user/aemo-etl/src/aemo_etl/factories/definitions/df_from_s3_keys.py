from collections.abc import Mapping
from typing import Iterable

from dagster import AssetIn, AutomationCondition, Definitions, asset
from dagster._core.definitions.assets.definition.asset_dep import CoercibleToAssetDep
from polars import LazyFrame, col, row_index, scan_delta
from polars._typing import PolarsDataType

from aemo_etl.configs import AEMO_BUCKET
from aemo_etl.factories.assets.df_from_s3_keys.factory import (
    df_from_s3_keys_asset_factory,
)
from aemo_etl.factories.assets.df_from_s3_keys.hooks import Hook
from aemo_etl.factories.checks.check_duplicate_rows import duplicate_row_check_factory
from aemo_etl.utils import get_metadata_schema, table_exists


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
) -> Definitions:

    bronze_asset = df_from_s3_keys_asset_factory(
        schema,
        schema_descriptions,
        surrogate_key_sources,
        postprocess_object_hooks=bronze_postprocess_object_hooks,
        postprocess_lazyframe_hooks=bronze_postprocess_lazyframe_hooks,
        key_prefix=(bronze_key_prefix := ["bronze", domain]),
        name=(bronze_table_name := f"bronze_{name_suffix}"),
        group_name=group_name,
        io_manager_key="aemo_deltalake_ingest_partitioned_append_io_manager",
        deps=deps,
        description=f"Bronze dataset, contains full un-cleansed dataset.\n\n{description}",
        metadata={
            "dagster/table_name": f"aemo.{domain}.{bronze_table_name}",
            "dagster/uri": f"s3://{AEMO_BUCKET}/{'/'.join(bronze_key_prefix)}/{bronze_table_name}",
            "glob_pattern": glob_pattern,
        },
    )

    # now create a silver asset which deduplicates the rows and cleans up the data
    @asset(
        group_name=group_name,
        key_prefix=(silver_key_prefix := ["silver", domain]),
        name=(silver_asset_name := f"silver_{name_suffix}"),
        ins={"df": AssetIn(bronze_asset.key)},
        io_manager_key="aemo_deltalake_append_io_manager",
        description=f"Silver dataset, contains deduplicated dataset.\n\n{description}",
        metadata={
            "dagster/column_schema": get_metadata_schema(schema, schema_descriptions),
            "surrogate_key_sources": surrogate_key_sources,
            "dagster/table_name": f"aemo.{domain}{silver_asset_name}",
            "dagster/uri": (
                silver_asset_uri
                := f"s3://{AEMO_BUCKET}/{'/'.join(silver_key_prefix)}/{silver_asset_name}"
            ),
        },
        kinds={"table", "deltalake"},
        automation_condition=AutomationCondition.any_deps_updated()
        & ~AutomationCondition.in_progress(),
    )
    def silver_asset(df: LazyFrame) -> LazyFrame:
        deduped_df = (
            df.with_columns(
                row_index().over("surrogate_key", order_by="ingested_timestamp")
            )
            .filter(col.index == 0)
            .drop("index")
        )

        if not table_exists(silver_asset_uri):
            return deduped_df

        latest = scan_delta(silver_asset_uri)

        max_date = latest.select(col.ingested_date.max()).collect().item()

        max_ts = (
            latest.filter(col.ingested_date == max_date)
            .select(col.ingested_timestamp.max())
            .collect()
            .item()
        )

        latest_keys = (
            latest.filter(
                (col.ingested_date >= max_date) & (col.ingested_timestamp >= max_ts)
            )
            .select("surrogate_key")
            .unique()
        )

        output = deduped_df.join(latest_keys, on="surrogate_key", how="anti")

        return output

    silver_asset_check = duplicate_row_check_factory(
        assets_definition=silver_asset,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description=f"Check that surrogate_key({surrogate_key_sources}) is unique",
    )

    return Definitions(
        assets=[bronze_asset, silver_asset], asset_checks=[silver_asset_check]
    )

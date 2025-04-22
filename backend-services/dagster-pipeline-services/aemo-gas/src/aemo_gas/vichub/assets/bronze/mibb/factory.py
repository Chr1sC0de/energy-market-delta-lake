from typing import Any
from typing import Iterable
from collections.abc import Callable

import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError

from aemo_gas import utils
from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET
from aemo_gas.vichub import assets


def delta_table(
    group_name: str,
    key_prefix: list[str],
    name: str,
    schema: dict[str, type],
    search_prefix: str,
    io_manager_key: str,
    bucket: str = LANDING_BUCKET,
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
    post_process_hook: Callable[[pl.LazyFrame], pl.LazyFrame] | None = None,
) -> dg.AssetsDefinition:
    @dg.op(
        name=f"{name}__get_s3_object_keys_from_prefix", ins={"start": dg.In(dg.Nothing)}
    )
    def get_s3_object_keys_from_prefix(
        context: dg.OpExecutionContext,
        s3_resource: S3Resource,
        # downloaded_public_files: pl.LazyFrame,
    ) -> list[str]:
        context.log.info(f"getting object keys s3://{bucket}/{search_prefix}*")
        s3_object_keys = utils.get_s3_object_keys_from_prefix(
            s3_resource, bucket, prefix=search_prefix
        )
        context.log.info(f"finished getting object keys s3://{bucket}/{search_prefix}*")
        return s3_object_keys

    @dg.op(
        name=f"{name}__get_dataframe",
        out={
            name: dg.Out(
                pl.LazyFrame,
                io_manager_key=io_manager_key,
                metadata=metadata,
            )
        },
    )
    def get_dataframe(
        context: dg.OpExecutionContext,
        s3_resource: S3Resource,
        s3_object_keys: list[str],
    ):
        context.log.info("combining asset keys into dataframe")
        df = utils.get_parquet_from_keys_and_combine_to_dataframe(
            context, s3_resource, s3_object_keys, schema, bucket
        )
        context.log.info("finished combining asset keys into dataframe")
        if post_process_hook is not None:
            context.log.info("applying post process hook to output df")
            df = post_process_hook(df)
            context.log.info("finished applying post process hook to output df")
        context.log.info("finished combining asset keys into dataframe")
        yield dg.Output(df, output_name=name)
        context.log.info("performing cleanup")
        s3_client = s3_resource.get_client()
        for key in s3_object_keys:
            context.log.info(f"removing s3://{bucket}/{key}")
            response = s3_client.delete_object(Bucket=LANDING_BUCKET, Key=key)
            context.log.info(
                f"ran delete_object for s3://{bucket}/{key} with response \n {response}"
            )

        context.log.info("finished prforming cleanup")

    @dg.graph_asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name=name,
        description=description,
        kinds={"deltalake"},
        ins={
            "downloaded_public_files": dg.AssetIn(
                assets.bronze.mibb.downloaded_public_files.asset.key
            )
        },
    )
    def asset(downloaded_public_files: pl.LazyFrame) -> pl.LazyFrame:
        s3_ojbect_keys = get_s3_object_keys_from_prefix(start=downloaded_public_files)
        df = get_dataframe(s3_ojbect_keys)
        return df

    return asset


def compact_and_vacuum(
    table_definition: dg.AssetsDefinition,
    group_name: str,
    key_prefix: list[str],
    table_name: str,
    retention_hours: int = 0,
    automation_condition: dg.AutomationCondition[Any] | None = None,
):
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name="compact_and_vacuum",
        description=f"compact and vacuum for {table_name}",
        deps=[table_definition],
        kinds={"task"},
        automation_condition=automation_condition,
    )
    def _compact_and_vacuum(context: dg.AssetExecutionContext):
        delta_table_path = f"{BRONZE_AEMO_GAS_DIRECTORY}/{'/'.join(key_prefix[-2:])}"

        context.log.info(f"running compact and vacuum for {delta_table_path}")

        try:
            delta_table = DeltaTable(delta_table_path)
        except TableNotFoundError:
            context.log.info(f"table not found {delta_table_path}")
            raise

        metadata = {}

        compacted_response = delta_table.optimize.compact()

        for key, value in compacted_response.items():
            metadata[key] = value

        metadata["vacuumed"] = delta_table.vacuum(
            retention_hours=retention_hours,
            enforce_retention_duration=False,
            dry_run=False,
        )

        context.add_asset_metadata(metadata)

    return _compact_and_vacuum

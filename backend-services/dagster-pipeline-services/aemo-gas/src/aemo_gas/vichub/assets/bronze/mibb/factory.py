import datetime as dt
from typing import Any

import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError
from types_boto3_s3 import S3Client

from aemo_gas import utils
from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET
from aemo_gas.vichub.assets import downloaded_files_metadata

metadata_table = f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/downloaded_files_metadata/"


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
) -> dg.AssetsDefinition:
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name=name,
        io_manager_key=io_manager_key,
        description=description,
        metadata=metadata,
        kinds={"deltalake"},
        deps=[downloaded_files_metadata.asset],
    )
    def _table(
        context: dg.AssetExecutionContext, s3_resource: S3Resource
    ) -> pl.LazyFrame:
        s3_object_keys = utils.get_s3_object_keys_op_from_prefix(
            s3_resource, bucket, search_prefix
        )
        return utils.get_parquet_from_keys_and_combine_to_dataframe_op(
            context, s3_resource, s3_object_keys, schema, bucket
        )

    return _table


def update_metadata(
    table_definition: dg.AssetsDefinition,
    group_name: str,
    key_prefix: list[str],
    name: str,
    search_prefix: str,
    bucket: str = LANDING_BUCKET,
) -> dg.AssetsDefinition:
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name="update_metadata_table",
        automation_condition=dg.AutomationCondition.eager(),
        description=f"update the processed datetime in the {metadata_table} for {name}",
        deps=[table_definition],
        kinds={"task"},
    )
    def _update_metadata(s3_resource: S3Resource):
        s3_object_keys = utils.get_s3_object_keys_op_from_prefix(
            s3_resource, bucket, search_prefix
        )

        delta_table = DeltaTable(metadata_table)

        for target_file in [f"s3://{bucket}/{key}" for key in s3_object_keys]:
            _ = delta_table.update(
                predicate=f"target_file = '{target_file}'",
                updates={
                    "processed_datetime": dt.datetime.now().strftime(
                        "TO_TIMESTAMP('%Y-%m-%d %H:%M:%S')"
                    )
                },
            )

    return _update_metadata


def cleanup_files(
    update_metadata_definition: dg.AssetsDefinition,
    group_name: str,
    key_prefix: list[str],
    name: str,
    search_prefix: str,
    bucket: str = LANDING_BUCKET,
) -> dg.AssetsDefinition:
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name="cleanup_files",
        automation_condition=dg.AutomationCondition.eager(),
        description=f"cleanup residual files for {name}",
        deps=[update_metadata_definition],
        kinds={"task"},
    )
    def _cleanup(context: dg.AssetExecutionContext, s3_resource: S3Resource):
        s3_client: S3Client = s3_resource.get_client()
        s3_object_keys = utils.get_s3_object_keys_op_from_prefix(
            s3_resource, bucket, search_prefix
        )

        for key in s3_object_keys:
            _ = s3_client.delete_object(Bucket=LANDING_BUCKET, Key=key)
        context.add_asset_metadata(
            {"removed_files": [f"{LANDING_BUCKET}/{k}" for k in s3_object_keys]}
        )

    return _cleanup


def compact_and_vacuum(
    table_definition: dg.AssetsDefinition,
    group_name: str,
    key_prefix: list[str],
    table_name: str,
    retention_hours: int = 0,
):
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name="compact_and_vacuum",
        description=f"compact and vacuum for {table_name}",
        deps=[table_definition],
        kinds={"task"},
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

from typing import Callable, Generator, Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    Output,
    asset,
)
from dagster_aws.s3 import S3Resource
from polars import LazyFrame

from aemo_etl.factory.asset.param_spec import AssetDefinitonParamSpec
from aemo_etl.util import (
    get_df_from_s3_keys,
    get_s3_object_keys_from_prefix_and_name_glob,
)


def get_df_from_s3_files_asset_factory(
    s3_source_bucket: str,
    s3_source_prefix: str,
    s3_source_file_glob: str,
    post_process_hook: Callable[[AssetExecutionContext, LazyFrame], LazyFrame]
    | None = None,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    asset_kwargs.setdefault("kinds", {"s3", "table", "deltalake"})

    @asset(**asset_kwargs)
    def get_df_from_s3_files_asset(
        context: AssetExecutionContext,
        s3: S3Resource,
    ) -> Generator[Output[LazyFrame]]:
        s3_client = s3.get_client()
        s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3_client=s3_client,
            s3_bucket=s3_source_bucket,
            s3_prefix=s3_source_prefix,
            s3_file_glob=s3_source_file_glob,
            case_insensitive=True,
            logger=context.log,
        )
        df = get_df_from_s3_keys(
            s3_client=s3_client,
            s3_bucket=s3_source_bucket,
            s3_object_keys=s3_object_keys,
            logger=context.log,
        )
        if post_process_hook is not None:
            df = post_process_hook(context, df)

        yield Output(df)
        # cleanup the data from the source bucket
        context.log.info("performing cleanup")
        s3_client = s3.get_client()

        for key in s3_object_keys:
            source_path = f"s3://{s3_source_bucket}/{key}"
            context.log.info(f"removing {source_path}")
            response = s3_client.delete_object(Bucket=s3_source_bucket, Key=key)
            context.log.info(
                f"ran delete_object for {source_path} with response \n {response}"
            )

    return get_df_from_s3_files_asset

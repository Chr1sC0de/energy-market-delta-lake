from dataclasses import dataclass
from typing import Callable, Generator, Mapping, Unpack

from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    MetadataValue,
    Output,
    asset,
)
from dagster_aws.s3 import S3Resource
from deltalake.exceptions import TableNotFoundError
from polars import LazyFrame, read_delta
from polars._typing import PolarsDataType

from aemo_etl.factory.asset.schema import DeltaIOManagedAssetKwargs
from aemo_etl.util import (
    get_df_from_s3_keys,
    get_s3_object_keys_from_prefix_and_name_glob,
)


@dataclass
class MetadataBuilder:
    table_uri: str

    def __call__(
        self,
        context: AssetExecutionContext,
        current_df: LazyFrame,
    ) -> dict[str, MetadataValue]:
        metadata = {}

        try:
            df_preview = read_delta(self.table_uri).lazy()
        except TableNotFoundError:
            df_preview = current_df

        df_markdown = df_preview.head().collect().to_pandas().to_markdown()

        assert df_markdown is not None

        metadata["preview"] = MetadataValue.md(df_markdown)
        return metadata


def get_mibb_report_from_s3_files_asset_factory(
    s3_source_bucket: str,
    s3_source_prefix: str,
    s3_source_file_glob: str,
    table_schema: Mapping[str, PolarsDataType] | None = None,
    post_process_hook: Callable[[AssetExecutionContext, LazyFrame], LazyFrame]
    | None = None,
    context_metadata_builder: MetadataBuilder | None = None,
    **asset_kwargs: Unpack[DeltaIOManagedAssetKwargs],
) -> AssetsDefinition:
    asset_kwargs.setdefault("kinds", {"s3", "table", "deltalake"})

    @asset(**asset_kwargs)
    def get_mibb_report_from_s3_files_asset(
        context: AssetExecutionContext,
        s3_resource: S3Resource,
    ) -> Generator[Output[LazyFrame]]:
        s3_client = s3_resource.get_client()
        s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3_client=s3_client,
            s3_bucket=s3_source_bucket,
            s3_prefix=s3_source_prefix,
            s3_file_glob=s3_source_file_glob,
            case_insensitive=True,
        )
        df = get_df_from_s3_keys(
            s3_client=s3_client,
            s3_bucket=s3_source_bucket,
            s3_object_keys=s3_object_keys,
            df_schema=table_schema,
            logger=context.log,
        )
        if post_process_hook is not None:
            df = post_process_hook(context, df)

        metadata: dict[str, MetadataValue] = {}

        if context_metadata_builder is not None:
            metadata = metadata | context_metadata_builder(
                context,
                df,
            )

        yield Output(df, metadata=metadata)
        # cleanup the data from the source bucket
        context.log.info("performing cleanup")
        s3_client = s3_resource.get_client()

        for key in s3_object_keys:
            source_path = f"s3://{s3_source_bucket}/{key}"
            context.log.info(f"removing {source_path}")
            response = s3_client.delete_object(Bucket=s3_source_bucket, Key=key)
            context.log.info(
                f"ran delete_object for {source_path} with response \n {response}"
            )

    return get_mibb_report_from_s3_files_asset

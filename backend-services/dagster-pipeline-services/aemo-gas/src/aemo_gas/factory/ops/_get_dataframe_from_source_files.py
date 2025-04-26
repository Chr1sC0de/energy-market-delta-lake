import abc
from typing import Any, Callable, Generator

import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource

from aemo_gas import utils


class GetDataFrameFromSourceFilesMetaDataBuilderBase(abc.ABC):
    @abc.abstractmethod
    def __call__(
        self,
        context: dg.OpExecutionContext,
        current_df: pl.LazyFrame,
        source_bucket: str,
        target_bucket: str,
        target_s3_prefix: str,
        target_name: str,
        df_schema: dict[str, pl.DataType],
        op_metadata: dict[str, Any],
    ) -> dict[str, dg.MetadataValue]: ...


def get_dataframe_from_source_files(
    source_bucket: str,
    target_bucket: str,
    target_s3_prefix: str,
    target_name: str,
    io_manager_key: str,  # this should be a io_manager which handles polars dataframes and outputs them to a delta table
    df_schema: dict[str, type[pl.DataType]],
    metadata: dict[str, Any] | None = None,
    post_process_hook: Callable[[pl.LazyFrame], pl.LazyFrame] | None = None,
    metadata_builders: list[GetDataFrameFromSourceFilesMetaDataBuilderBase]
    | None = None,
) -> dg.OpDefinition:
    @dg.op(
        name="get_dataframe",
        out={
            target_name: dg.Out(
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
    ) -> Generator[dg.Output[pl.LazyFrame]]:
        # get the df from the source bucket using the extracted s3_object_keys
        context.log.info("combining asset keys into dataframe")
        df = utils.get_df_from_s3_keys(
            context, s3_resource, s3_object_keys, df_schema, source_bucket
        )
        context.log.info("finished combining asset keys into dataframe")
        if post_process_hook is not None:
            context.log.info("applying post process hook to output df")
            df = post_process_hook(df)
            context.log.info("finished applying post process hook to output df")
        context.log.info("finished combining asset keys into dataframe")

        # write the dataframe to the target bucket using the target_s3_prefix
        metadata: dict[str, dg.MetadataValue] = {}

        if metadata_builders is not None:
            for builder in metadata_builders:
                metadata = metadata | builder(
                    context,
                    df,
                    source_bucket,
                    target_bucket,
                    target_s3_prefix,
                    target_name,
                    df_schema,
                    op_metadata=metadata,
                )

        yield dg.Output(df, output_name=target_name, metadata=metadata)

        # cleanup the data from the source bucket
        context.log.info("performing cleanup")
        s3_client = s3_resource.get_client()

        for key in s3_object_keys:
            source_path = f"s3://{source_bucket}/{key}"
            context.log.info(f"removing {source_path}")
            response = s3_client.delete_object(Bucket=source_bucket, Key=key)
            context.log.info(
                f"ran delete_object for {source_path} with response \n {response}"
            )
        context.log.info("finished prforming cleanup")

    return get_dataframe

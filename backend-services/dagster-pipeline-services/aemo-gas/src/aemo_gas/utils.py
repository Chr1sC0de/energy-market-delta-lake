import datetime as dt

import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource
from deltalake import DeltaTable
from types_boto3_s3.client import S3Client

from aemo_gas.configurations import LANDING_BUCKET


def join_by_newlines(*args: str) -> str:
    return "\n".join(args)


def get_s3_object_keys_op_from_prefix(
    s3_resource: S3Resource,
    bucket: str,
    prefix: str,
) -> list[str]:
    s3_client: S3Client = s3_resource.get_client()
    paginator = s3_client.get_paginator("list_objects_v2")
    s3_objects = []
    for page in paginator.paginate(Bucket=bucket, Prefix="aemo/gas/vichub/"):
        if "Contents" in page:
            s3_objects.extend(
                [
                    f["Key"]
                    for f in page["Contents"]
                    if f["Key"].lower().split("/")[-1].startswith(prefix)
                ]
            )
    return s3_objects


def get_parquet_from_keys_and_combine_to_dataframe_op(
    context: dg.OpExecutionContext | dg.AssetExecutionContext,
    s3_resource: S3Resource,
    s3_object_keys: list[str],
    schema: dict[str, type],
    bucket: str,
) -> pl.LazyFrame:
    s3_client = s3_resource.get_client()
    all_dfs: list[pl.LazyFrame] = []
    for key in s3_object_keys:
        object_bytes = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
        if len(object_bytes) > 0:
            df = pl.read_parquet(object_bytes)
            if "source_file" not in df.columns:
                df = df.with_columns(
                    pl.col(c).cast(schema[c]) for c in df.columns
                ).with_columns(
                    pl.lit(f"S3://{LANDING_BUCKET}/{key}").alias("source_file")
                )
            all_dfs.append(df)
        else:
            context.log.info(f"{key} contains 0 bytes")

    if len(all_dfs) == 0:
        return pl.LazyFrame(schema=schema)

    return pl.concat(all_dfs, how="diagonal_relaxed").lazy()


def update_download_metadata_table_op(
    target_files: list[str], delta_table_path: str
) -> tuple[list[str], pl.LazyFrame]:
    for target_file in target_files:
        delta_table = DeltaTable(delta_table_path)

        _ = delta_table.update(
            predicate=f"target_file = '{target_file}'",
            updates={
                "processed_datetime": dt.datetime.now().strftime(
                    "TO_TIMESTAMP('%Y-%m-%d %H:%M:%S')"
                )
            },
        )

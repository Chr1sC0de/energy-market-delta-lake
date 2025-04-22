import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource
from deltalake.exceptions import TableNotFoundError
from types_boto3_s3.client import S3Client


def join_by_newlines(*args: str) -> str:
    return "\n".join(args)


def get_table(table_path: str) -> pl.LazyFrame | None:
    try:
        df = pl.read_delta(table_path, use_pyarrow=True).lazy()
    except TableNotFoundError:
        df = None
    return df


def get_s3_object_keys_from_prefix(
    s3_resource: S3Resource,
    bucket: str,
    schema: str,
    prefix: str,
) -> list[str]:
    s3_client: S3Client = s3_resource.get_client()
    paginator = s3_client.get_paginator("list_objects_v2")
    s3_objects = []
    for page in paginator.paginate(Bucket=bucket, Prefix=f"aemo/gas/{schema}/"):
        if "Contents" in page:
            s3_objects.extend(
                [
                    f["Key"]
                    for f in page["Contents"]
                    if f["Key"].lower().split("/")[-1].startswith(prefix)
                ]
            )
    return s3_objects


def get_s3_object_keys_from_suffix_case_insensitive(
    s3_resource: S3Resource,
    bucket: str,
    suffix: str,
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
                    if f["Key"].lower().split("/")[-1].lower().endswith(suffix)
                ]
            )
    return s3_objects


def get_parquet_from_keys_and_combine_to_dataframe(
    context: dg.OpExecutionContext | dg.AssetExecutionContext,
    s3_resource: S3Resource,
    s3_object_keys: list[str],
    schema: dict[str, type],
    bucket: str,
) -> pl.LazyFrame:
    s3_client = s3_resource.get_client()
    all_dfs: list[pl.LazyFrame] = []

    for key in s3_object_keys:
        context.log.info(f"processing s3://{bucket}/{key}")
        try:
            object_bytes = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
            if len(object_bytes) > 0:
                df = pl.read_parquet(object_bytes).unique().lazy()
                df = df.with_columns(
                    pl.col(c).cast(schema[c]) for c in df.columns
                ).with_columns(pl.lit(f"S3://{bucket}/{key}").alias("source_file"))
                all_dfs.append(df)
            else:
                context.log.info(f"{key} contains 0 bytes")
        except Exception:
            context.log.info(f"failed to get {key}")

    if len(all_dfs) == 0:
        context.log.info("no valid dataframes found returning empty dataframe")
        return pl.LazyFrame(schema=schema)

    return pl.concat(all_dfs, how="diagonal_relaxed")

import dagster as dg
import polars as pl
import fnmatch
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


def get_s3_object_keys_from_prefix_and_name_glob(
    s3_resource: S3Resource,
    bucket: str,
    prefix: str,
    file_glob: str,
) -> list[str]:
    s3_client: S3Client = s3_resource.get_client()
    paginator = s3_client.get_paginator("list_objects_v2")
    s3_objects = []
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" in page:
            original_keys = [c["Key"] for c in page["Contents"]]
            case_insensitive_keys = [k.lower() for k in original_keys]
            mapping = {ik: ok for ik, ok in zip(case_insensitive_keys, original_keys)}
            filtered_insensitive_keys = fnmatch.filter(
                case_insensitive_keys, f"{prefix}/{file_glob}"
            )
            s3_objects.extend([mapping[k] for k in filtered_insensitive_keys])
    return s3_objects


def get_df_from_s3_keys(
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
                if key.lower().endswith(".parquet"):
                    df = pl.read_parquet(object_bytes).unique().lazy()
                elif key.lower().endswith(".csv"):
                    df = (
                        pl.read_csv(object_bytes, infer_schema_length=None)
                        .unique()
                        .lazy()
                    )
                else:
                    raise ValueError(f"filetype of {key} is unsupported")

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

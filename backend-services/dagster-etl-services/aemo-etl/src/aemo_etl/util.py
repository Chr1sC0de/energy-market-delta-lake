import fnmatch
from collections.abc import Generator, Mapping
from logging import Logger
from math import ceil
from typing import Callable, cast

import polars as pl
from botocore.exceptions import ClientError
from botocore.paginate import PageIterator
from dagster import TableColumn, TableSchema
from polars._typing import PolarsDataType
from types_boto3_s3 import S3Client


def newline_join(*args: str, extra: str | None = None) -> str:
    if extra is None:
        extra = ""
    return f"\n{extra}".join(args)


def get_s3_pagination(
    s3_client: S3Client,
    s3_bucket: str,
    s3_prefix: str,
    logger: Logger | None = None,
) -> list[PageIterator]:
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = []
    if logger is not None:
        logger.info(f"getting pages for 's3://{s3_bucket}/{s3_prefix}'")
    for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
        pages.append(page)

    if logger is not None:
        logger.info(f"total pages found {len(pages)}")

    return pages


def get_s3_object_keys_from_prefix_and_name_glob(
    s3_client: S3Client,
    s3_bucket: str,
    s3_prefix: str,
    s3_file_glob: str,
    case_insensitive: bool = True,
    pages: list[PageIterator] | None = None,
    logger: Logger | None = None,
) -> list[str]:
    """given a key prefix and a globbing pattern get all the s3 object keys"""

    s3_objects: list[str] = []
    if pages is None:
        pages = get_s3_pagination(s3_client, s3_bucket, s3_prefix, logger=logger)

    if logger is not None:
        logger.info(f"grabbing files from s3://{s3_bucket}/{s3_prefix}/{s3_file_glob}")

    number_of_pages = len(pages)

    for i, page in enumerate(pages):
        if logger is not None:
            logger.info(f"processing page {i + 1} of {number_of_pages}")
        if "Contents" in page:
            original_keys = [c["Key"] for c in page["Contents"]]  # type: ignore[not-subscriptable]
            if case_insensitive:
                case_insensitive_keys = [k.lower() for k in original_keys]
                mapping = {
                    ik: ok for ik, ok in zip(case_insensitive_keys, original_keys)
                }
                filtered_insensitive_keys = fnmatch.filter(
                    case_insensitive_keys, f"{s3_prefix}/{s3_file_glob}"
                )
                s3_objects.extend([mapping[k] for k in filtered_insensitive_keys])
            else:
                s3_objects.extend(
                    fnmatch.filter(original_keys, f"{s3_prefix}/{s3_file_glob}")
                )
    if logger is not None:
        logger.info(f"found {s3_objects}")
    return s3_objects


def get_df_from_s3_keys(
    s3_client: S3Client,
    s3_bucket: str,
    s3_object_keys: list[str],
    table_schema: Mapping[str, PolarsDataType] | None = None,
    process_object_hook: Callable[[Logger | None, bytes], pl.LazyFrame] | None = None,
    df_hook: Callable[[Logger | None, pl.LazyFrame], pl.LazyFrame] | None = None,
    logger: Logger | None = None,
) -> pl.LazyFrame:
    all_dfs: list[pl.LazyFrame] = []

    for key in s3_object_keys:
        if logger is not None:
            logger.info(f"processing s3://{s3_bucket}/{key}")
        try:
            object_bytes = s3_client.get_object(Bucket=s3_bucket, Key=key)[
                "Body"
            ].read()

            if len(object_bytes) > 0:
                df = None

                if process_object_hook is not None:
                    df = process_object_hook(logger, object_bytes)
                elif key.lower().endswith(".parquet"):
                    df = pl.read_parquet(object_bytes, missing_columns="insert").lazy()
                elif key.lower().endswith(".csv"):
                    df = pl.read_csv(object_bytes, infer_schema_length=None).lazy()
                else:
                    if logger is not None:
                        logger.info(f"filetype of {key} is unsupported")

                if df is not None:
                    df = df.with_columns(
                        pl.lit(f"s3://{s3_bucket}/{key}").alias("source_file")
                    )
                    if df_hook is not None:
                        df = df_hook(logger, df)
                    if table_schema is not None:
                        df = df.with_columns(
                            pl.col(c).cast(d)
                            for c, d in table_schema.items()
                            if c in df.collect_schema()
                        )
                    all_dfs.append(df)
            else:
                if logger is not None:
                    logger.info(f"{key} contains 0 bytes")
        except ClientError as e:
            if logger is not None:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.info(f"key {key} does not exist")

    if len(all_dfs) == 0:
        if logger is not None:
            logger.info("no valid dataframes found returning empty dataframe")
        return pl.LazyFrame(schema=table_schema)

    if table_schema is not None:
        # this will help to fill out any missing columns
        return pl.concat(
            [pl.LazyFrame(schema=table_schema), *all_dfs], how="diagonal_relaxed"
        )

    return pl.concat(all_dfs, how="diagonal_relaxed")


def get_metadata_schema(
    df_schema: Mapping[str, type[pl.DataType]] | pl.Schema,
    descriptions: Mapping[str, str] | None = None,
) -> TableSchema:
    descriptions = descriptions or {}
    return TableSchema(
        columns=[
            TableColumn(name=col, type=str(pl_type), description=descriptions.get(col))
            for col, pl_type in df_schema.items()
        ]
    )


def get_lazyframe_num_rows(df: pl.LazyFrame) -> int:
    return cast(pl.DataFrame, df.select(pl.len()).collect()).item()


def split_list[T](list_: list[T], num_chunks: int) -> Generator[list[T]]:
    len_list = len(list_)
    split_size = max(1, ceil(len_list / num_chunks))
    if len_list == 0:
        return
    else:
        for i in range(0, len_list, split_size):
            yield list_[i : i + split_size]

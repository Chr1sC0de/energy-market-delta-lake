import datetime as dt
import fnmatch
import uuid
from collections.abc import Callable, Mapping
from datetime import datetime
from logging import Logger
from typing import Protocol, TypedDict, cast

import polars as pl
import polars_hash as plh
import requests
from botocore.exceptions import ClientError
from dagster import TableColumn, TableSchema
from deltalake import DeltaTable
from polars import (
    Expr,
    LazyFrame,
    Schema,
    scan_csv,
    scan_parquet,
)
from polars import len as len_
from polars._typing import PolarsDataType
from requests import RequestException, Response
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)
from types_boto3_s3 import S3Client
from types_boto3_s3.type_defs import ListObjectsV2OutputTypeDef

# NOTE:
#
# Dagster’s component system:
#
# - walks module attributes
# - calls predicates on them
# - accidentally hits Polars Expr
# - Python tries bool(expr)
#
# This is a known friction point between:
#
# - lazy expression libraries (Polars)
# - introspection-heavy frameworks (Dagster, Pydantic, etc.)
#
# this is why we will use pl.col over col directly

AEST = dt.timezone(dt.timedelta(hours=10))


def get_s3_pagination(
    s3_client: S3Client,
    s3_bucket: str,
    s3_prefix: str,
    logger: Logger | None = None,
) -> list[ListObjectsV2OutputTypeDef]:
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = []
    if logger is not None:
        logger.info(f"getting pages for 's3://{s3_bucket}/{s3_prefix}'")
    for page in paginator.paginate(Bucket=s3_bucket, Prefix=s3_prefix):
        pages.append(page)

    if logger is not None:
        logger.info(f"total pages found {len(pages)}")

    return pages


class S3ObjectHead(TypedDict, total=False):
    ChecksumAlgorithm: list[str]
    ChecksumType: str
    ETag: str
    Key: str
    LastModified: datetime
    Size: int
    StorageClass: str


def get_object_head_from_pages(
    pages: list[ListObjectsV2OutputTypeDef],
    logger: Logger | None = None,
) -> dict[str, S3ObjectHead]:
    number_of_pages = len(pages)
    output = {}
    for i, page in enumerate(pages):
        if logger is not None:
            logger.info(f"processing page {i + 1} of {number_of_pages}")
        if "Contents" in page:
            for object_head in page["Contents"]:
                output[object_head["Key"]] = cast(S3ObjectHead, object_head)
    return output


def get_s3_object_keys_from_prefix_and_name_glob(
    s3_prefix: str,
    s3_file_glob: str,
    original_keys: list[str],
    case_insensitive: bool = True,
) -> list[str]:
    s3_objects = []
    if case_insensitive:
        case_insensitive_keys = [k.lower() for k in original_keys]
        mapping = {ik: ok for ik, ok in zip(case_insensitive_keys, original_keys)}
        filtered_insensitive_keys = fnmatch.filter(
            case_insensitive_keys, f"{s3_prefix}/{s3_file_glob}"
        )
        s3_objects.extend([mapping[k] for k in filtered_insensitive_keys])
    else:
        s3_objects.extend(fnmatch.filter(original_keys, f"{s3_prefix}/{s3_file_glob}"))
    return s3_objects


def get_metadata_schema(
    df_schema: Mapping[str, PolarsDataType | type[object]] | Schema,
    descriptions: Mapping[str, str] | None = None,
) -> TableSchema:
    descriptions = descriptions or {}
    return TableSchema(
        columns=[
            TableColumn(name=col, type=str(pl_type), description=descriptions.get(col))
            for col, pl_type in df_schema.items()
        ]
    )


def request_get(
    path: str, getter: Callable[[str], Response] = requests.get
) -> Response:
    response: Response = getter(path)
    response.raise_for_status()
    return response


def add_random_suffix(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def get_lazyframe_num_rows(df: LazyFrame) -> int:
    return cast(int, df.select(len_()).collect(engine="streaming").item())  # ty:ignore[unresolved-attribute]


def get_surrogate_key(primary_keys: list[str] | list[Expr]) -> Expr:
    expressions = []
    for key in primary_keys:
        if isinstance(key, str):
            expressions.append(pl.col(key))
        elif isinstance(key, Expr):
            expressions.append(key)
        else:
            raise TypeError(
                f"{key.__class__} is an invalid type should be either str or polars.Expr"
            )
    return plh.concat_str(
        *[expression.fill_null("") for expression in expressions]
    ).chash.sha2_256()


class BytesToLazyFrameMethod(Protocol):
    def __call__(self, bytes_: bytes) -> LazyFrame: ...


BYTES_TO_LAZYFRAME_REGISTER: dict[str, BytesToLazyFrameMethod] = {}


def register_bytes_to_lazyframe_method(
    filetype: str,
) -> Callable[[BytesToLazyFrameMethod], BytesToLazyFrameMethod]:
    def _register_bytes_to_lazyframe_method(
        function: BytesToLazyFrameMethod,
    ) -> BytesToLazyFrameMethod:
        BYTES_TO_LAZYFRAME_REGISTER[filetype] = function
        return function

    return _register_bytes_to_lazyframe_method


@register_bytes_to_lazyframe_method("csv")
def csv_bytes_to_lazyframe(bytes_: bytes) -> LazyFrame:
    return scan_csv(bytes_, infer_schema_length=None)


@register_bytes_to_lazyframe_method("parquet")
def parquet_bytes_to_lazyframe(bytes_: bytes) -> LazyFrame:
    return scan_parquet(bytes_)


def bytes_to_lazyframe(filetype: str, bytes_: bytes) -> LazyFrame:
    return BYTES_TO_LAZYFRAME_REGISTER[filetype](bytes_)


def get_from_s3(
    s3_client: S3Client, s3_bucket: str, s3_key: str, logger: Logger | None = None
) -> bytes | None:
    try:
        bytes_ = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)["Body"].read()
    except ClientError as e:
        if logger is not None:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"key {s3_key} does not exist")
            else:
                logger.error(
                    f"unable to process {s3_key} for bucket {s3_bucket} with error {e}"
                )
        bytes_ = None
    return bytes_


def table_exists(s3_table_location: str) -> bool:
    return DeltaTable.is_deltatable(s3_table_location)


def get_response_factory(
    process_retry: int = 3,
    initial: int = 10,
    exp_base: int = 3,
    max_retry_time: int = 100,
) -> Callable[[str], bytes]:

    @retry(
        stop=stop_after_attempt(process_retry),
        wait=wait_exponential_jitter(
            initial=initial, exp_base=exp_base, max=max_retry_time
        ),
        retry=retry_if_exception_type(RequestException),
        reraise=True,
    )
    def get_bytes(link: str) -> bytes:
        return request_get(link).content

    return get_bytes

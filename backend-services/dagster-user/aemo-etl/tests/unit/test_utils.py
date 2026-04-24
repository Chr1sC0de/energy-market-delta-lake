import io
from logging import Logger

import polars as pl
import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client
from types_boto3_s3.type_defs import ListObjectsV2OutputTypeDef, ObjectTypeDef

from aemo_etl.utils import (
    add_random_suffix,
    bytes_to_lazyframe,
    csv_bytes_to_lazyframe,
    get_from_s3,
    get_lazyframe_num_rows,
    get_metadata_schema,
    get_object_head_from_pages,
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
    get_surrogate_key,
    parquet_bytes_to_lazyframe,
    request_get,
    table_exists,
)

# ---------------------------------------------------------------------------
# Existing tests (kept intact)
# ---------------------------------------------------------------------------


def test_pagination(mocker: MockerFixture) -> None:
    class PaginatorMock:
        @staticmethod
        def paginate(**_: object) -> list[object]:
            return ["mock", "mock"]

    s3_client = mocker.MagicMock(spec=S3Client)
    logger = mocker.MagicMock(spec=Logger)
    s3_client.get_paginator.return_value = PaginatorMock
    get_s3_pagination(s3_client, "mock", "mock", logger)


def test_get_object_head_from_pages(mocker: MockerFixture) -> None:
    mocked_pages: list[ListObjectsV2OutputTypeDef] = [
        {"Contents": [mocker.MagicMock(spec=ObjectTypeDef) for _ in range(5)]}  # type: ignore[typeddict-item]
        for _ in range(5)
    ]
    get_object_head_from_pages(mocked_pages, logger=mocker.MagicMock(spec=Logger))


@pytest.mark.parametrize("case_insensitive", [True, False])
def test_get_s3_object_keys_from_prefix_and_name_glob(case_insensitive: bool) -> None:
    mocked_keys = ["mock_1", "mock_2"]
    get_s3_object_keys_from_prefix_and_name_glob(
        s3_prefix="mock",
        s3_file_glob="mock*",
        original_keys=mocked_keys,
        case_insensitive=case_insensitive,
    )


# ---------------------------------------------------------------------------
# New tests for previously uncovered lines
# ---------------------------------------------------------------------------


def test_pagination_no_logger(mocker: MockerFixture) -> None:
    """get_s3_pagination with logger=None skips the log.info calls."""

    class PaginatorMock:
        @staticmethod
        def paginate(**_: object) -> list[object]:
            return ["p1"]

    s3_client = mocker.MagicMock(spec=S3Client)
    s3_client.get_paginator.return_value = PaginatorMock
    pages = get_s3_pagination(s3_client, "bucket", "prefix")
    assert len(pages) == 1


def test_get_object_head_from_pages_no_logger(mocker: MockerFixture) -> None:
    mocked_pages: list[ListObjectsV2OutputTypeDef] = [
        {"Contents": [mocker.MagicMock(spec=ObjectTypeDef) for _ in range(2)]}  # type: ignore[typeddict-item]
    ]
    result = get_object_head_from_pages(mocked_pages)
    assert len(result) == 2


def test_get_metadata_schema_with_descriptions() -> None:
    schema = {"col_a": pl.String, "col_b": pl.Int64}
    descriptions = {"col_a": "first col", "col_b": "second col"}
    result = get_metadata_schema(schema, descriptions)
    assert len(result.columns) == 2
    col_names = [c.name for c in result.columns]
    assert "col_a" in col_names
    assert "col_b" in col_names


def test_get_metadata_schema_no_descriptions() -> None:
    schema = {"col_a": pl.String}
    result = get_metadata_schema(schema)
    assert result.columns[0].name == "col_a"


def test_request_get_success(mocker: MockerFixture) -> None:
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.return_value = None
    getter = mocker.MagicMock(return_value=mock_response)
    result = request_get("https://example.com", getter=getter)
    assert result is mock_response
    mock_response.raise_for_status.assert_called_once()


def test_request_get_raises(mocker: MockerFixture) -> None:
    import requests

    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("bad")
    getter = mocker.MagicMock(return_value=mock_response)
    with pytest.raises(requests.HTTPError):
        request_get("https://example.com", getter=getter)


def test_add_random_suffix() -> None:
    result = add_random_suffix("my-prefix")
    assert result.startswith("my-prefix-")
    assert len(result) == len("my-prefix-") + 8


def test_get_lazyframe_num_rows() -> None:
    df = pl.LazyFrame({"a": [1, 2, 3]})
    assert get_lazyframe_num_rows(df) == 3


def test_get_surrogate_key_str_keys() -> None:
    df = pl.LazyFrame({"col1": ["a", "b"], "col2": ["x", "y"]})
    expr = get_surrogate_key(["col1", "col2"])
    result = df.with_columns(sk=expr).collect()
    assert len(result["sk"]) == 2
    # Both should be non-empty hashes
    assert all(len(h) > 0 for h in result["sk"])


def test_get_surrogate_key_expr_keys() -> None:
    df = pl.LazyFrame({"col1": ["a"]})
    expr = get_surrogate_key([pl.col("col1")])
    result = df.with_columns(sk=expr).collect()
    assert len(result["sk"]) == 1


def test_get_surrogate_key_invalid_type() -> None:
    with pytest.raises(TypeError):
        get_surrogate_key([123])  # type: ignore[arg-type]


def _make_parquet_bytes() -> bytes:
    buf = io.BytesIO()
    pl.DataFrame({"a": [1, 2]}).write_parquet(buf)
    return buf.getvalue()


_CSV_BYTES = b"col1,col2\nval1,val2\n"
_PARQUET_BYTES = _make_parquet_bytes()


def test_csv_bytes_to_lazyframe() -> None:
    lf = csv_bytes_to_lazyframe(_CSV_BYTES)
    assert isinstance(lf, pl.LazyFrame)
    assert "col1" in lf.collect_schema().names()


def test_parquet_bytes_to_lazyframe() -> None:
    lf = parquet_bytes_to_lazyframe(_PARQUET_BYTES)
    assert isinstance(lf, pl.LazyFrame)
    assert "a" in lf.collect_schema().names()


def test_bytes_to_lazyframe_csv() -> None:
    lf = bytes_to_lazyframe("csv", _CSV_BYTES)
    assert isinstance(lf, pl.LazyFrame)


def test_bytes_to_lazyframe_parquet() -> None:
    lf = bytes_to_lazyframe("parquet", _PARQUET_BYTES)
    assert isinstance(lf, pl.LazyFrame)


def test_get_from_s3_success(mocker: MockerFixture) -> None:
    s3_client = mocker.MagicMock(spec=S3Client)
    s3_client.get_object.return_value = {"Body": mocker.MagicMock(read=lambda: b"data")}
    result = get_from_s3(s3_client, "bucket", "key")
    assert result == b"data"


def test_get_from_s3_no_such_key_with_logger(mocker: MockerFixture) -> None:
    logger = mocker.MagicMock(spec=Logger)
    s3_client = mocker.MagicMock(spec=S3Client)
    err = ClientError({"Error": {"Code": "NoSuchKey", "Message": "x"}}, "GetObject")
    s3_client.get_object.side_effect = err
    result = get_from_s3(s3_client, "bucket", "key", logger=logger)
    assert result is None
    logger.error.assert_called_once()


def test_get_from_s3_other_error_with_logger(mocker: MockerFixture) -> None:
    logger = mocker.MagicMock(spec=Logger)
    s3_client = mocker.MagicMock(spec=S3Client)
    err = ClientError({"Error": {"Code": "AccessDenied", "Message": "x"}}, "GetObject")
    s3_client.get_object.side_effect = err
    result = get_from_s3(s3_client, "bucket", "key", logger=logger)
    assert result is None
    logger.error.assert_called_once()


def test_get_from_s3_no_such_key_no_logger(mocker: MockerFixture) -> None:
    s3_client = mocker.MagicMock(spec=S3Client)
    err = ClientError({"Error": {"Code": "NoSuchKey", "Message": "x"}}, "GetObject")
    s3_client.get_object.side_effect = err
    result = get_from_s3(s3_client, "bucket", "key")
    assert result is None


def test_table_exists_true(mocker: MockerFixture) -> None:
    mocker.patch(
        "aemo_etl.utils.DeltaTable.is_deltatable",
        return_value=True,
    )
    assert table_exists("s3://bucket/table") is True


def test_table_exists_false(mocker: MockerFixture) -> None:
    mocker.patch(
        "aemo_etl.utils.DeltaTable.is_deltatable",
        return_value=False,
    )
    assert table_exists("s3://bucket/missing") is False

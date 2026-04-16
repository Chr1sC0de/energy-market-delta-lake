import logging
from datetime import datetime, timezone
from unittest.mock import Mock, patch

import polars as pl
import pytest
from requests import HTTPError, Response
from types_boto3_s3 import S3Client

from aemo_etl.utils import (
    get_from_s3,
    get_lazyframe_num_rows,
    get_object_head_from_pages,
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
    request_get,
    table_exists,
)
from tests.utils import MakeBucketProtocol

logger = logging.getLogger(__name__)


def test_request_get_success() -> None:
    mock_response = Mock(spec=Response)
    mock_response.status_code = 200
    mock_response.raise_for_status = Mock()

    mock_getter = Mock(return_value=mock_response)

    result = request_get("https://example.com", getter=mock_getter)

    assert result == mock_response
    mock_getter.assert_called_once_with("https://example.com")
    mock_response.raise_for_status.assert_called_once()


def test_request_get_raises_http_error() -> None:
    mock_response = Mock(spec=Response)
    mock_response.status_code = 404
    mock_response.raise_for_status = Mock(side_effect=HTTPError("Not Found"))

    mock_getter = Mock(return_value=mock_response)

    with pytest.raises(HTTPError):
        request_get("https://example.com/notfound", getter=mock_getter)

    mock_getter.assert_called_once_with("https://example.com/notfound")
    mock_response.raise_for_status.assert_called_once()


def test_get_lazyframe_num_rows() -> None:
    df = pl.LazyFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    result = get_lazyframe_num_rows(df)

    assert result == 3


def test_get_from_s3(
    s3: S3Client, make_bucket: MakeBucketProtocol, caplog: pytest.LogCaptureFixture
) -> None:
    bucket_name = make_bucket("test-bucket")
    with caplog.at_level(logging.ERROR):
        get_from_s3(s3, bucket_name, "fake-item", logger=logger)
    assert caplog.messages[-1] == "key fake-item does not exist"


def test_get_s3_pagination_with_logger(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket_name = make_bucket("test-pagination")
    mock_logger = Mock()
    pages = get_s3_pagination(s3, bucket_name, "some/prefix", logger=mock_logger)
    assert isinstance(pages, list)
    mock_logger.info.assert_called()


def test_get_s3_pagination_without_logger(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket_name = make_bucket("test-pagination-no-log")
    pages = get_s3_pagination(s3, bucket_name, "some/prefix")
    assert isinstance(pages, list)


def test_get_object_head_from_pages_with_contents() -> None:
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    pages = [
        {
            "Contents": [
                {
                    "Key": "prefix/file1.csv",
                    "ETag": "abc",
                    "LastModified": now,
                    "Size": 100,
                    "StorageClass": "STANDARD",
                }
            ]
        }
    ]
    result = get_object_head_from_pages(pages)  # type: ignore[arg-type]
    assert "prefix/file1.csv" in result
    assert result["prefix/file1.csv"]["Size"] == 100


def test_get_object_head_from_pages_with_logger() -> None:
    mock_logger = Mock()
    pages: list[object] = [{"Contents": [{"Key": "k", "Size": 1}]}]
    result = get_object_head_from_pages(pages, logger=mock_logger)  # type: ignore[arg-type]
    assert "k" in result
    mock_logger.info.assert_called()


def test_get_object_head_from_pages_empty() -> None:
    pages: list[object] = [{}]
    result = get_object_head_from_pages(pages)  # type: ignore[arg-type]
    assert result == {}


def test_get_s3_object_keys_case_insensitive() -> None:
    keys = ["PREFIX/File1.CSV", "prefix/file2.csv", "other/file3.csv"]
    result = get_s3_object_keys_from_prefix_and_name_glob(
        "prefix", "*.csv", keys, case_insensitive=True
    )
    assert set(result) == {"PREFIX/File1.CSV", "prefix/file2.csv"}


def test_get_s3_object_keys_case_sensitive() -> None:
    keys = ["prefix/file1.CSV", "prefix/file2.csv"]
    result = get_s3_object_keys_from_prefix_and_name_glob(
        "prefix", "*.csv", keys, case_insensitive=False
    )
    assert result == ["prefix/file2.csv"]


def test_table_exists_false() -> None:
    with patch("aemo_etl.utils.DeltaTable") as mock_dt:
        mock_dt.is_deltatable.return_value = False
        assert table_exists("s3://fake-bucket/fake-table") is False


def test_table_exists_true() -> None:
    with patch("aemo_etl.utils.DeltaTable") as mock_dt:
        mock_dt.is_deltatable.return_value = True
        assert table_exists("s3://fake-bucket/real-table") is True

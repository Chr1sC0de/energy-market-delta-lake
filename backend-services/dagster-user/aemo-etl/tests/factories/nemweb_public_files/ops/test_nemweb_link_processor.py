from datetime import datetime
from io import BytesIO

import pytest
from dagster import OpExecutionContext, build_op_context
from dagster_aws.s3 import S3Resource
from polars import read_parquet
from requests import Response

from aemo_etl.configs import AEMO_BUCKET, LANDING_BUCKET
from aemo_etl.factories.nemweb_public_files.data_models import (
    Link,
    ProcessedLink,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_processor import (
    BufferProcessor,
    NEMWebLinkProcessor,
    ParquetProcessor,
    S3NemwebLinkProcessor,
    build_nemweb_link_processor_op,
)
from tests.utils import MakeBucketProtocol


@pytest.fixture
def mock_link() -> Link:
    return Link(
        source_absolute_href="https://example.com.au/reports/test_file.csv",
        source_upload_datetime=datetime(year=2025, month=1, day=1),
    )


class MockBufferProcessor(BufferProcessor):
    def process(
        self,
        context: OpExecutionContext,
        link: Link,
    ) -> tuple[BytesIO, str]:
        content = b"test,data,content\n1,2,3\n4,5,6"
        upload_filename = link.source_absolute_href.rsplit("/", 1)[-1].lower()
        return (BytesIO(content), upload_filename)


@pytest.fixture
def mock_buffer_processor() -> MockBufferProcessor:
    return MockBufferProcessor()


@pytest.fixture
def mock_s3_resource(localstack_endpoint: str) -> S3Resource:
    return S3Resource(endpoint_url=localstack_endpoint)


def test_csv_buffer_processor() -> None:
    class MockCSVResponse(Response):
        @property
        def content(self) -> bytes:
            content = b"test,data,content\n1,2,3\n4,5,6"
            return content

    parquet_processor = ParquetProcessor(request_getter=lambda x: MockCSVResponse())
    data = parquet_processor.process(
        build_op_context(), Link(source_absolute_href="mock.csv")
    )

    assert read_parquet(data[0]) is not None


def test_non_csv_buffer_processor(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str] = []

    class MockCSVResponse(Response):
        @property
        def content(self) -> bytes:
            content = b"a,b\n\nc,d,e,f,g\nh,i,j,k,l"
            return content

    def info(content: str) -> None:
        captured.append(content)

    context = build_op_context()
    monkeypatch.setattr(context.log, "info", info)
    parquet_processor = ParquetProcessor(request_getter=lambda x: MockCSVResponse())
    parquet_processor.process(context, Link(source_absolute_href="mock.csv"))
    assert "failed to convert" in captured[0]


def test_build_nemweb_link_processor_op(
    mock_link: Link, mock_s3_resource: S3Resource
) -> None:
    class MockNEMWebLinkProcessor(NEMWebLinkProcessor):
        def process(
            self,
            context: OpExecutionContext,
            s3: S3Resource,
            link: Link,
            s3_target_bucket: str,
            s3_target_prefix: str,
        ) -> ProcessedLink:
            return ProcessedLink(
                source_absolute_href=link.source_absolute_href,
                source_upload_datetime=link.source_upload_datetime,
                target_s3_href="s3://test-bucket/test-prefix/test_file.csv",
                target_s3_bucket="test-bucket",
                target_s3_prefix="test-prefix",
                target_s3_name="test_file.csv",
                target_ingested_datetime=datetime(year=2025, month=1, day=2),
            )

    processor_op = build_nemweb_link_processor_op(
        "mock", "test-bucket", "test-prefix", MockNEMWebLinkProcessor()
    )

    result = processor_op(build_op_context(), mock_s3_resource, mock_link)

    assert result.source_absolute_href == "https://example.com.au/reports/test_file.csv"
    assert result.target_s3_href == "s3://test-bucket/test-prefix/test_file.csv"
    assert result.target_s3_bucket == "test-bucket"
    assert result.target_s3_prefix == "test-prefix"
    assert result.target_s3_name == "test_file.csv"


class TestS3NemwebLinkProcessor:
    def test_process_uploads_to_s3(
        self,
        mock_link: Link,
        mock_buffer_processor: MockBufferProcessor,
        mock_s3_resource: S3Resource,
        make_bucket: MakeBucketProtocol,
    ) -> None:
        bronze_bucket_name = make_bucket(AEMO_BUCKET)
        s3_prefix = "test-prefix"

        processor = S3NemwebLinkProcessor(
            buffer_processor=mock_buffer_processor,
        )

        result = processor.process(
            build_op_context(),
            mock_s3_resource,
            mock_link,
            s3_target_bucket=bronze_bucket_name,
            s3_target_prefix=s3_prefix,
        )

        assert result.source_absolute_href == mock_link.source_absolute_href
        assert result.source_upload_datetime == mock_link.source_upload_datetime
        assert result.target_s3_bucket == bronze_bucket_name
        assert result.target_s3_prefix == s3_prefix
        assert result.target_s3_name == "test_file.csv"
        assert (
            result.target_s3_href
            == f"s3://{bronze_bucket_name}/{s3_prefix}/test_file.csv"
        )
        assert isinstance(result.target_ingested_datetime, datetime)

        s3_client = mock_s3_resource.get_client()
        response = s3_client.get_object(
            Bucket=bronze_bucket_name, Key=f"{s3_prefix}/test_file.csv"
        )
        content = response["Body"].read()
        assert content == b"test,data,content\n1,2,3\n4,5,6"

    def test_process_lowercases_filename(
        self,
        mock_buffer_processor: MockBufferProcessor,
        mock_s3_resource: S3Resource,
        make_bucket: MakeBucketProtocol,
    ) -> None:
        bucket_name = make_bucket(LANDING_BUCKET)
        s3_prefix = "test-prefix"

        link_uppercase = Link(
            source_absolute_href="https://example.com.au/reports/TEST_FILE_UPPER.CSV",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        )

        processor = S3NemwebLinkProcessor(
            buffer_processor=mock_buffer_processor,
        )

        result = processor.process(
            build_op_context(),
            mock_s3_resource,
            link_uppercase,
            bucket_name,
            s3_prefix,
        )

        assert result.target_s3_name == "test_file_upper.csv"
        assert (
            result.target_s3_href
            == f"s3://{bucket_name}/{s3_prefix}/test_file_upper.csv"
        )

        s3_client = mock_s3_resource.get_client()
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_prefix)
        assert "Contents" in response
        assert len(response["Contents"]) == 1
        assert response["Contents"][0]["Key"] == f"{s3_prefix}/test_file_upper.csv"

    def test_process_extracts_filename_from_url(
        self,
        mock_buffer_processor: MockBufferProcessor,
        mock_s3_resource: S3Resource,
        make_bucket: MakeBucketProtocol,
    ) -> None:
        bucket_name = make_bucket(LANDING_BUCKET)
        s3_prefix = "test-prefix"

        link_nested_path = Link(
            source_absolute_href="https://example.com.au/reports/2025/01/nested_file.zip",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        )

        processor = S3NemwebLinkProcessor(
            buffer_processor=mock_buffer_processor,
        )

        result = processor.process(
            build_op_context(),
            mock_s3_resource,
            link_nested_path,
            bucket_name,
            s3_prefix,
        )

        assert result.target_s3_name == "nested_file.zip"
        assert (
            result.target_s3_href == f"s3://{bucket_name}/{s3_prefix}/nested_file.zip"
        )

    def test_process_with_none_upload_datetime(
        self,
        mock_buffer_processor: MockBufferProcessor,
        mock_s3_resource: S3Resource,
        make_bucket: MakeBucketProtocol,
    ) -> None:
        bucket_name = make_bucket(LANDING_BUCKET)
        s3_prefix = "test-prefix"

        link_no_datetime = Link(
            source_absolute_href="https://example.com.au/reports/file.csv",
            source_upload_datetime=None,
        )

        processor = S3NemwebLinkProcessor(
            buffer_processor=mock_buffer_processor,
        )

        result = processor.process(
            build_op_context(),
            mock_s3_resource,
            link_no_datetime,
            bucket_name,
            s3_prefix,
        )

        assert result.source_upload_datetime is None
        assert result.target_s3_name == "file.csv"
        assert isinstance(result.target_ingested_datetime, datetime)

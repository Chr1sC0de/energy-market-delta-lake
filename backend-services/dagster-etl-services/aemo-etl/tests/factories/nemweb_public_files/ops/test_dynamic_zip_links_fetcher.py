from typing import Generator
from unittest.mock import Mock

from dagster import DynamicOutput, OpExecutionContext, build_op_context
from dagster_aws.s3 import S3Resource

from aemo_etl.factories.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    DynamicZipLinksFetcher,
    S3DynamicZipLinksFetcher,
    build_dynamic_zip_link_fetcher_op,
)


def test_build_dynamic_zip_link_fetcher_op(localstack_endpoint: str) -> None:
    class MockDynamicZipLinksFetcher(DynamicZipLinksFetcher):
        def fetch(
            self,
            s3_landing_bucket: str,
            s3_landing_prefix: str,
            context: OpExecutionContext,
            s3: S3Resource,
        ) -> Generator[DynamicOutput[str]]:
            yield DynamicOutput("test/file1.zip", mapping_key="file1_zip")
            yield DynamicOutput("test/file2.zip", mapping_key="file2_zip")

    op_def = build_dynamic_zip_link_fetcher_op(
        "test",
        "test-bucket",
        "test-prefix",
        MockDynamicZipLinksFetcher(),
    )

    s3_resource = S3Resource(endpoint_url=localstack_endpoint)
    context = build_op_context(
        resources={"s3": s3_resource},
        op_config={},
    )

    results = list(op_def(context))

    assert len(results) == 2
    assert results[0].value == "test/file1.zip"
    assert results[0].mapping_key == "file1_zip"
    assert results[1].value == "test/file2.zip"
    assert results[1].mapping_key == "file2_zip"


class TestS3DynamicZipLinksFetcher:
    def test_fetch_with_zip_files(self) -> None:
        mock_s3_client = Mock()
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {
                "Contents": [
                    {"Key": "test-prefix/file1.zip"},
                    {"Key": "test-prefix/file2.ZIP"},
                    {"Key": "test-prefix/file3.csv"},
                ]
            }
        ]

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        fetcher = S3DynamicZipLinksFetcher()
        context = build_op_context()

        results = list(fetcher.fetch("test-bucket", "test-prefix", context, mock_s3))

        assert len(results) == 2
        assert results[0].value == "test-prefix/file1.zip"
        assert results[0].mapping_key == "file1_zip"
        assert results[1].value == "test-prefix/file2.ZIP"
        assert results[1].mapping_key == "file2_ZIP"

        mock_s3_client.get_paginator.assert_called_once_with("list_objects_v2")
        mock_s3_client.get_paginator.return_value.paginate.assert_called_once_with(
            Bucket="test-bucket", Prefix="test-prefix"
        )

    def test_fetch_no_contents(self) -> None:
        mock_s3_client = Mock()
        mock_s3_client.get_paginator.return_value.paginate.return_value = [{}]

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        fetcher = S3DynamicZipLinksFetcher()
        context = build_op_context()

        results = list(fetcher.fetch("test-bucket", "test-prefix", context, mock_s3))

        assert len(results) == 0

    def test_fetch_multiple_pages(self) -> None:
        mock_s3_client = Mock()
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "test-prefix/file1.zip"}]},
            {"Contents": [{"Key": "test-prefix/file2.zip"}]},
        ]

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        fetcher = S3DynamicZipLinksFetcher()
        context = build_op_context()

        results = list(fetcher.fetch("test-bucket", "test-prefix", context, mock_s3))

        assert len(results) == 2

    def test_fetch_special_characters_in_key(self) -> None:
        mock_s3_client = Mock()
        mock_s3_client.get_paginator.return_value.paginate.return_value = [
            {"Contents": [{"Key": "test-prefix/file-with-special@chars#123.zip"}]}
        ]

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        fetcher = S3DynamicZipLinksFetcher()
        context = build_op_context()

        results = list(fetcher.fetch("test-bucket", "test-prefix", context, mock_s3))

        assert len(results) == 1
        assert results[0].value == "test-prefix/file-with-special@chars#123.zip"
        assert results[0].mapping_key == "file_with_special_chars_123_zip"

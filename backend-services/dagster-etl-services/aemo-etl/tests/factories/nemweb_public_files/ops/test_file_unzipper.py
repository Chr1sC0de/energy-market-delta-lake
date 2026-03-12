from io import BytesIO
from typing import Any
from unittest.mock import Mock, patch
from zipfile import ZipFile

from dagster import OpExecutionContext, build_op_context
from dagster_aws.s3 import S3Resource

from aemo_etl.factories.nemweb_public_files.ops.file_unzipper import (
    FileUnzipper,
    S3FileUnzipper,
    build_unzip_files_op,
)


def test_build_unzip_files_op(localstack_endpoint: str) -> None:
    class MockFileUnzipper(FileUnzipper):
        def unzip(
            self,
            context: OpExecutionContext,
            s3: S3Resource,
            s3_source_key: str,
            s3_target_bucket: str,
            s3_target_prefix: str,
        ) -> list[dict[str, str]]:
            return [
                {"Bucket": s3_target_bucket, "Key": f"{s3_target_prefix}/file1.csv"},
                {"Bucket": s3_target_bucket, "Key": f"{s3_target_prefix}/file2.csv"},
            ]

    op_def = build_unzip_files_op(
        "test",
        "test-bucket",
        "test-prefix",
        MockFileUnzipper(),
    )

    s3_resource = S3Resource(endpoint_url=localstack_endpoint)
    context = build_op_context(
        resources={"s3": s3_resource},
        op_config={},
    )

    results = op_def(context, s3_source_key="test/archive.zip")

    assert len(results) == 2
    assert results[0]["Bucket"] == "test-bucket"
    assert results[0]["Key"] == "test-prefix/file1.csv"
    assert results[1]["Bucket"] == "test-bucket"
    assert results[1]["Key"] == "test-prefix/file2.csv"


class TestS3FileUnzipper:
    def create_zip_file(self, files: dict[str, bytes]) -> BytesIO:
        """Helper to create a zip file in memory."""
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zf:
            for filename, content in files.items():
                zf.writestr(filename, content)
        zip_buffer.seek(0)
        return zip_buffer

    def test_unzip_csv_files_converts_to_parquet(self) -> None:
        csv_content = b"col1,col2\nval1,val2\nval3,val4"
        zip_buffer = self.create_zip_file({"test.csv": csv_content})

        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: zip_buffer.getvalue())
        }
        mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

        uploaded_files: list[dict[str, Any]] = []

        def mock_upload(buffer: BytesIO, bucket: str, key: str) -> None:
            uploaded_files.append({"buffer": buffer, "bucket": bucket, "key": key})

        mock_s3_client.upload_fileobj.side_effect = mock_upload

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/test.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 1
        assert results[0]["Bucket"] == "test-bucket"
        assert results[0]["Key"] == "target-prefix/test.parquet"

        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="source/test.zip"
        )
        mock_s3_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="source/test.zip"
        )

    def test_unzip_non_csv_files(self) -> None:
        txt_content = b"This is a text file"
        zip_buffer = self.create_zip_file({"test.txt": txt_content})

        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: zip_buffer.getvalue())
        }
        mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

        uploaded_files: list[dict[str, Any]] = []

        def mock_upload(buffer: BytesIO, bucket: str, key: str) -> None:
            uploaded_files.append({"buffer": buffer, "bucket": bucket, "key": key})

        mock_s3_client.upload_fileobj.side_effect = mock_upload

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/test.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 1
        assert results[0]["Bucket"] == "test-bucket"
        assert results[0]["Key"] == "target-prefix/test.txt"

    def test_unzip_multiple_files(self) -> None:
        files = {
            "file1.csv": b"col1,col2\nval1,val2",
            "file2.txt": b"text content",
            "file3.csv": b"colA,colB\nvalA,valB",
        }
        zip_buffer = self.create_zip_file(files)

        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: zip_buffer.getvalue())
        }
        mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/test.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 3
        result_keys = {r["Key"] for r in results}
        assert "target-prefix/file1.parquet" in result_keys
        assert "target-prefix/file2.txt" in result_keys
        assert "target-prefix/file3.parquet" in result_keys

    def test_unzip_skips_directories(self) -> None:
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zf:
            zf.writestr("folder/", "")
            zf.writestr("folder/file.txt", b"content")

        zip_buffer.seek(0)

        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: zip_buffer.getvalue())
        }
        mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/test.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 1
        assert results[0]["Key"] == "target-prefix/folder/file.txt"

    def test_unzip_handles_no_such_key(self) -> None:
        mock_s3_client = Mock()
        mock_s3_client.exceptions.NoSuchKey = type("NoSuchKey", (Exception,), {})
        mock_s3_client.get_object.side_effect = mock_s3_client.exceptions.NoSuchKey()

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/nonexistent.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 0
        mock_s3_client.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="source/nonexistent.zip"
        )

    @patch("aemo_etl.factories.nemweb_public_files.ops.file_unzipper.read_csv")
    def test_unzip_csv_conversion_fails_uses_original(
        self, mock_read_csv: Mock
    ) -> None:
        mock_read_csv.side_effect = ValueError("CSV parsing failed")

        invalid_csv = b"not,a,valid\ncsv,content"
        zip_buffer = self.create_zip_file({"invalid.csv": invalid_csv})

        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            "Body": Mock(read=lambda: zip_buffer.getvalue())
        }
        mock_s3_client.delete_object.return_value = {"DeleteMarker": True}

        uploaded_files: list[dict[str, Any]] = []

        def mock_upload(buffer: BytesIO, bucket: str, key: str) -> None:
            uploaded_files.append({"buffer": buffer, "bucket": bucket, "key": key})
            buffer.seek(0)
            content = buffer.read()
            if key.endswith(".csv"):
                assert content == invalid_csv

        mock_s3_client.upload_fileobj.side_effect = mock_upload

        mock_s3 = Mock(spec=S3Resource)
        mock_s3.get_client.return_value = mock_s3_client

        unzipper = S3FileUnzipper()
        context = build_op_context()

        results = unzipper.unzip(
            context,
            mock_s3,
            "source/test.zip",
            "test-bucket",
            "target-prefix",
        )

        assert len(results) == 1
        assert results[0]["Key"] == "target-prefix/invalid.csv"

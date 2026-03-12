from abc import ABC, abstractmethod
from io import BytesIO
from zipfile import ZipFile

from dagster import (
    Backoff,
    In,
    Jitter,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    RetryPolicy,
    op,
)
from dagster_aws.s3 import S3Resource
from polars import read_csv
from types_boto3_s3 import S3Client


class FileUnzipper(ABC):
    @abstractmethod
    def unzip(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        s3_source_key: str,
        s3_target_bucket: str,
        s3_target_prefix: str,
    ) -> list[dict[str, str]]: ...


def build_unzip_files_op(
    name: str,
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    file_unzippper: FileUnzipper,
    retry_policy: RetryPolicy = RetryPolicy(
        max_retries=3,
        delay=0.2,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS,
    ),
) -> OpDefinition:
    @op(
        name=f"{name}_unzip_s3_file_from_key_op",
        description=f"unzips all files in s3://{s3_landing_bucket}/{s3_landing_prefix}",
        retry_policy=retry_policy,
        ins={"start": In(Nothing)},
    )
    def _op(
        context: OpExecutionContext,
        s3: S3Resource,
        s3_source_key: str,
    ) -> list[dict[str, str]]:
        return file_unzippper.unzip(
            context, s3, s3_source_key, s3_landing_bucket, s3_landing_prefix
        )

    return _op


class S3FileUnzipper(FileUnzipper):
    def unzip(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        s3_source_key: str,
        s3_target_bucket: str,
        s3_target_prefix: str,
    ) -> list[dict[str, str]]:
        unzipped_files: list[dict[str, str]] = []

        context.log.info(f"processing zip file s3://{s3_target_bucket}/{s3_source_key}")

        s3_client: S3Client = s3.get_client()
        try:
            get_object_response = s3_client.get_object(
                Bucket=s3_target_bucket, Key=s3_source_key
            )

            s3_object_bytes_io = BytesIO(get_object_response["Body"].read())

            with ZipFile(s3_object_bytes_io) as f:
                for file_name in f.namelist():
                    if not file_name.endswith("/"):
                        buffer = BytesIO(f.read(file_name))

                        extension = file_name.lower().split(".")[-1]

                        original_buffer = buffer
                        original_filename = file_name

                        try:
                            # if the extension of the file is csv convert it into a parquet file  # noqa: E501
                            if extension == "csv":
                                file_name = file_name.lower().replace(
                                    ".csv", ".parquet"
                                )
                                csv_df = read_csv(buffer, infer_schema_length=None)
                                buffer = BytesIO()
                                csv_df.write_parquet(buffer)
                        except Exception as e:
                            context.log.info(
                                f"failed to convert from csv to parquet format, using original format with error message {e}"  # noqa: E501
                            )
                            buffer = original_buffer
                            file_name = original_filename

                        write_key = f"{s3_target_prefix}/{file_name}"

                        _ = buffer.seek(0)

                        s3_client.upload_fileobj(buffer, s3_target_bucket, write_key)
                        unzipped_files.append(
                            {"Bucket": s3_target_bucket, "Key": write_key}
                        )

            get_object_response = s3_client.delete_object(
                Bucket=s3_target_bucket, Key=s3_source_key
            )

            context.log.info(
                f"processed s3://{s3_target_bucket}/{s3_source_key}, sending files to s3://{s3_target_bucket}/{s3_target_prefix}."
            )
            context.log.info(
                f"finished cleaning file with delete_object response: {get_object_response}"  # noqa: E501
            )
        except s3_client.exceptions.NoSuchKey:
            context.log.info(f"no key found s3://{s3_target_bucket}/{s3_source_key}")

        return unzipped_files

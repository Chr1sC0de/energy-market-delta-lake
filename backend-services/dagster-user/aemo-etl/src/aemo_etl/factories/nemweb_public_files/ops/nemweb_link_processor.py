from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Callable

from dagster import Backoff, Jitter, OpDefinition, OpExecutionContext, RetryPolicy, op
from dagster_aws.s3 import S3Resource
from polars import read_csv
from requests import Response
from types_boto3_s3 import S3Client

from aemo_etl.factories.nemweb_public_files.models import (
    Link,
    ProcessedLink,
)
from aemo_etl.utils import AEST, request_get


class NEMWebLinkProcessor(ABC):
    @abstractmethod
    def process(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        links: list[Link],
        s3_target_bucket: str,
        s3_target_prefix: str,
    ) -> list[ProcessedLink]: ...


def build_nemweb_link_processor_op(
    name: str,
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    nemweb_link_processor: NEMWebLinkProcessor,
    retry_policy: RetryPolicy = RetryPolicy(
        max_retries=3,
        delay=0.2,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS,
    ),
) -> OpDefinition:

    @op(
        name=f"{name}_nemweb_link_processor_op",
        description=f"download file from a link and upload into s3://{s3_landing_bucket}/{s3_landing_prefix}",
        retry_policy=retry_policy,
    )
    def _op(
        context: OpExecutionContext,
        s3: S3Resource,
        links: list[Link],
    ) -> list[ProcessedLink]:
        return nemweb_link_processor.process(
            context,
            s3,
            links,
            s3_landing_bucket,
            s3_landing_prefix,
        )

    return _op


class BufferProcessor(ABC):
    @abstractmethod
    def process(
        self,
        context: OpExecutionContext,
        link: Link,
    ) -> tuple[BytesIO, str]: ...

    """returns a tuple of the output buffer and the upload filename"""


@dataclass
class ParquetProcessor(BufferProcessor):
    request_getter: Callable[[str], Response] = request_get

    def process(
        self,
        context: OpExecutionContext,
        link: Link,
    ) -> tuple[BytesIO, str]:
        path = link.source_absolute_href
        response = self.request_getter(path)
        link_buffer = BytesIO(response.content)
        upload_filename = link.source_absolute_href.rsplit("/", 1)[-1].lower()

        name, extension = upload_filename.rsplit(".", 1)

        upload_filename = (
            f"{name}~{datetime.now().strftime('%y%m%d%H%M%S')}.{extension}"
        )

        original_buffer = link_buffer
        original_upload_filename = upload_filename

        try:
            if extension == "csv":
                upload_filename = upload_filename.replace(".csv", ".parquet")
                csv_df = read_csv(link_buffer, infer_schema_length=None)
                link_buffer = BytesIO()
                csv_df.write_parquet(link_buffer)
        except Exception as e:
            context.log.info(
                f"failed to convert from csv to parquet format, using original format with error message {e}"
            )
            link_buffer = original_buffer
            upload_filename = original_upload_filename

        return (link_buffer, upload_filename)


@dataclass
class S3NemwebLinkProcessor(NEMWebLinkProcessor):
    buffer_processor: BufferProcessor

    def process(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        links: list[Link],
        s3_target_bucket: str,
        s3_target_prefix: str,
    ) -> list[ProcessedLink]:
        s3_client: S3Client = s3.get_client()

        output: list[ProcessedLink] = []

        def process_link(link: Link) -> None:
            context.log.info(f"processing {link.source_absolute_href}")

            link_buffer, upload_filename = self.buffer_processor.process(context, link)

            link_buffer.seek(0)

            s3_client.upload_fileobj(
                link_buffer,
                s3_target_bucket,
                f"{s3_target_prefix}/{upload_filename}",
            )

            target_s3_href = (
                f"s3://{s3_target_bucket}/{s3_target_prefix}/{upload_filename}"
            )

            processed_link = ProcessedLink(
                source_absolute_href=link.source_absolute_href,
                source_upload_datetime=link.source_upload_datetime,
                target_s3_href=target_s3_href,
                target_s3_bucket=s3_target_bucket,
                target_s3_prefix=s3_target_prefix,
                target_s3_name=upload_filename,
                target_ingested_datetime=datetime.now(AEST),
            )

            context.log.info(
                f"finished processing and uploading {link.source_absolute_href} to {target_s3_href}"
            )

            output.append(processed_link)

        with ThreadPoolExecutor() as executor:
            executor.map(process_link, links)

        return output

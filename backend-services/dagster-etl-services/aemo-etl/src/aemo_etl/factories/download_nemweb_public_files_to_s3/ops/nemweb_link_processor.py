from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Callable

from dagster import OpDefinition, OpExecutionContext, op
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.factories.download_nemweb_public_files_to_s3.data_models import (
    Link,
    ProcessedLink,
)
from aemo_etl.configs import LANDING_BUCKET


class NEMWebLinkProcessor(ABC):
    @abstractmethod
    def process(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        link: Link,
    ) -> ProcessedLink: ...


def build_nemweb_link_processor_op(
    name: str,
    s3_source_bucket: str,
    s3_source_prefix: str,
    nemweb_link_processor: NEMWebLinkProcessor,
) -> OpDefinition:

    @op(
        name=f"{name}_nemweb_link_processor_op",
        description=f"download file from a link and upload into s3://{s3_source_bucket}/{s3_source_prefix}",
    )
    def _op(
        context: OpExecutionContext,
        s3: S3Resource,
        link: Link,
    ) -> ProcessedLink:
        return nemweb_link_processor.process(context, s3, link)

    return _op


@dataclass
class S3NemwebLinkProcessor(NEMWebLinkProcessor):
    s3_landing_prefix: str
    buffer_processor: Callable[[Link], BytesIO]
    s3_landing_bucket: str = LANDING_BUCKET

    def process(
        self,
        context: OpExecutionContext,
        s3: S3Resource,
        link: Link,
    ) -> ProcessedLink:
        s3_client: S3Client = s3.get_client()

        context.log.info(f"processing {link.source_absolute_href}")

        link_buffer = self.buffer_processor(link)

        upload_filename = link.source_absolute_href.rsplit("/", 1)[-1].lower()

        _ = link_buffer.seek(0)

        s3_client.upload_fileobj(
            link_buffer,
            self.s3_landing_bucket,
            f"{self.s3_landing_prefix}/{upload_filename}",
        )

        target_s3_href = (
            f"s3://{self.s3_landing_bucket}/{self.s3_landing_prefix}/{upload_filename}"
        )

        processed_link = ProcessedLink(
            source_absolute_href=link.source_absolute_href,
            source_upload_datetime=link.source_upload_datetime,
            target_s3_href=target_s3_href,
            target_s3_bucket=self.s3_landing_bucket,
            target_s3_prefix=self.s3_landing_prefix,
            target_s3_name=upload_filename,
            target_ingested_datetime=datetime.now(),
        )

        context.log.info(
            f"finished processing and uploading {link.source_absolute_href} to {target_s3_href}"  # noqa: E501
        )
        return processed_link

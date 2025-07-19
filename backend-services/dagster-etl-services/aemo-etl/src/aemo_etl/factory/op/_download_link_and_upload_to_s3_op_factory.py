from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from typing import Unpack

import requests
from dagster import Backoff, Jitter, OpDefinition, OpExecutionContext, RetryPolicy, op
from dagster_aws.s3 import S3Resource
from polars import read_csv
from types_boto3_s3 import S3Client

from aemo_etl.configuration import Link, ProcessedLink
from aemo_etl.factory.op.schema import OpKwargs


def default_get_buffer_from_link(link: Link) -> BytesIO:
    response = requests.get(link.source_absolute_href)
    response.raise_for_status()
    return BytesIO(response.content)


def download_link_and_upload_to_s3_op_factory(
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    get_buffer_from_link_hook: Callable[[Link], BytesIO] | None = None,
    **op_kwargs: Unpack[OpKwargs],
) -> OpDefinition:
    op_kwargs.setdefault("name", "download_link_and_upload_to_s3_op")
    op_kwargs.setdefault(
        "retry_policy",
        RetryPolicy(
            max_retries=3,
            delay=0.2,  # 200ms
            backoff=Backoff.EXPONENTIAL,
            jitter=Jitter.PLUS_MINUS,
        ),
    )
    op_kwargs.setdefault(
        "description",
        f"download files from provded links and store in s3://{s3_landing_bucket}/{s3_landing_prefix}",
    )

    if get_buffer_from_link_hook is None:
        get_buffer_from_link_hook = default_get_buffer_from_link

    @op(**op_kwargs)
    def download_link_and_upload_to_s3_op(
        context: OpExecutionContext,
        s3: S3Resource,
        link: Link,
    ) -> ProcessedLink:
        s3_client: S3Client = s3.get_client()

        context.log.info(f"processing {link.source_absolute_href}")

        link_buffer = get_buffer_from_link_hook(link)

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

        _ = link_buffer.seek(0)

        s3_client.upload_fileobj(
            link_buffer,
            s3_landing_bucket,
            f"{s3_landing_prefix}/{upload_filename}",
        )

        target_s3_href = (
            f"s3://{s3_landing_bucket}/{s3_landing_prefix}/{upload_filename}"
        )

        processed_link = ProcessedLink(
            source_absolute_href=link.source_absolute_href,
            source_upload_datetime=link.source_upload_datetime,
            target_s3_href=target_s3_href,
            target_s3_bucket=s3_landing_bucket,
            target_s3_prefix=s3_landing_prefix,
            target_s3_name=upload_filename,
            target_ingested_datetime=datetime.now(),
        )

        context.log.info(
            f"finished processing and uploading {link.source_absolute_href} to {target_s3_href}"
        )
        return processed_link

    return download_link_and_upload_to_s3_op

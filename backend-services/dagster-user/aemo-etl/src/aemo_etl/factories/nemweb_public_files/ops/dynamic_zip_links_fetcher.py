import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generator

from dagster import (
    DynamicOut,
    DynamicOutput,
    In,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    op,
)
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client


class DynamicZipLinksFetcher(ABC):
    @abstractmethod
    def fetch(
        self,
        s3_landing_bucket: str,
        s3_landing_prefix: str,
        context: OpExecutionContext,
        s3: S3Resource,
    ) -> Generator[DynamicOutput[str]]: ...


def build_dynamic_zip_link_fetcher_op(
    name: str,
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    dynamic_zip_links_fetcher: DynamicZipLinksFetcher,
) -> OpDefinition:
    @op(
        ins={"start": In(Nothing)},
        out=DynamicOut(),
        name=f"{name}_dynamic_zip_link_fetcher_op",
        description=f"get list s3_keys from zip files in s3://{s3_landing_bucket}/{s3_landing_prefix}",
    )
    def _op(
        context: OpExecutionContext,
        s3: S3Resource,
    ) -> Generator[DynamicOutput[str]]:
        for fetched in dynamic_zip_links_fetcher.fetch(
            s3_landing_bucket,
            s3_landing_prefix,
            context,
            s3,
        ):
            yield fetched

    return _op


@dataclass
class S3DynamicZipLinksFetcher(DynamicZipLinksFetcher):
    def fetch(
        self,
        s3_landing_bucket: str,
        s3_landing_prefix: str,
        context: OpExecutionContext,
        s3: S3Resource,
    ) -> Generator[DynamicOutput[str]]:
        s3_client: S3Client = s3.get_client()
        paginator = s3_client.get_paginator("list_objects_v2")
        s3_objects = []
        for page in paginator.paginate(
            Bucket=s3_landing_bucket, Prefix=s3_landing_prefix
        ):
            if "Contents" in page:
                s3_objects.extend(
                    [f for f in page["Contents"] if f["Key"].lower().endswith(".zip")]
                )

        if len(s3_objects) > 0:
            context.log.info("ZIP files Found, Processing...")

        for s3_object in s3_objects:
            s3_object_key = s3_object["Key"]
            yield DynamicOutput[str](
                s3_object_key,
                mapping_key=re.sub("[^0-9a-zA-Z]+", "_", s3_object_key.split("/")[-1]),
            )

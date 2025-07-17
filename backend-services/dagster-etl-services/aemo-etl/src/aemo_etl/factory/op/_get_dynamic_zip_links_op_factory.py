import re
from collections.abc import Generator
from typing import Unpack

from dagster import DynamicOut, DynamicOutput, In, Nothing, OpExecutionContext, op
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.factory.op.schema import OpKwargs


def get_dyanmic_zip_links_op_factory(
    s3_source_bucket: str,
    s3_source_prefix: str,
    **op_kwargs: Unpack[OpKwargs],
):
    op_kwargs.setdefault("name", "get_dyanmic_zip_links_op")
    op_kwargs.setdefault("out", DynamicOut())
    op_kwargs.setdefault("ins", {"start": In(Nothing)})
    op_kwargs.setdefault(
        "description",
        f"get list s3_keys from zip files in  s3://{s3_source_bucket}/{s3_source_prefix}",
    )

    @op(**op_kwargs)
    def get_dynamic_links_zip_op(
        context: OpExecutionContext,
        s3: S3Resource,
    ) -> Generator[DynamicOutput[str]]:
        s3_client: S3Client = s3.get_client()
        paginator = s3_client.get_paginator("list_objects_v2")
        s3_objects = []
        for page in paginator.paginate(
            Bucket=s3_source_bucket, Prefix=s3_source_prefix
        ):
            if "Contents" in page:
                s3_objects.extend(
                    [f for f in page["Contents"] if f["Key"].lower().endswith(".zip")]  # pyright: ignore[reportTypedDictNotRequiredAccess]
                )

        if len(s3_objects) > 0:
            context.log.info("ZIP files Found, Processing...")

        for s3_object in s3_objects:
            s3_object_key = s3_object["Key"]
            yield DynamicOutput[str](
                s3_object_key,
                mapping_key=re.sub("[^0-9a-zA-Z]+", "_", s3_object_key.split("/")[-1]),
            )

    return get_dynamic_links_zip_op

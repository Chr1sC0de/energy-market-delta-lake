import datetime as dt
import io
import zipfile
from collections.abc import Generator

import dagster as dg
import polars as pl
from dagster_aws.s3 import S3Resource
from deltalake import DeltaTable
from types_boto3_s3.client import S3Client

from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │     for each zip file create update in the s3 bucket unzip the file and load it's      │
#     │                              contents into the s3 bucket                               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

delta_table_path = f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/downloaded_files_metadata/"


@dg.op(out=dg.DynamicOut())
def create_dynamic_process_zip_op(
    context: dg.OpExecutionContext,
    s3_resource: S3Resource,
) -> Generator[dg.DynamicOutput[str]]:
    s3_client: S3Client = s3_resource.get_client()
    paginator = s3_client.get_paginator("list_objects_v2")
    s3_objects = []
    for page in paginator.paginate(Bucket=LANDING_BUCKET, Prefix="aemo/gas/vichub/"):
        if "Contents" in page:
            s3_objects.extend(
                [f for f in page["Contents"] if f["Key"].lower().endswith(".zip")]
            )
    if len(s3_objects) > 0:
        context.log.info("ZIP files Found, Processing...")

    for s3_object in s3_objects:
        s3_object_key = s3_object["Key"]
        yield dg.DynamicOutput[str](
            s3_object_key,
            mapping_key=f"link_{s3_object_key.replace('/', '_').replace('~', '_').replace('.', '_')}",
        )


@dg.op(
    retry_policy=dg.RetryPolicy(
        max_retries=3,
        delay=0.2,  # 200ms
        backoff=dg.Backoff.EXPONENTIAL,
        jitter=dg.Jitter.PLUS_MINUS,
    )
)
def process_zip_op(
    context: dg.OpExecutionContext, s3_resource: S3Resource, key: str
) -> None:
    context.log.info(f"processing csv file {LANDING_BUCKET}/{key}")
    s3_client: S3Client = s3_resource.get_client()

    response = s3_client.get_object(Bucket=LANDING_BUCKET, Key=key)

    zip_io = io.BytesIO(response["Body"].read())

    context.log.info("extracting files and uploading to s3")

    with zipfile.ZipFile(zip_io) as f:
        for name in f.namelist():
            data = f.read(name)
            dataframe_buffer = io.BytesIO()
            dataframe = pl.read_csv(data, infer_schema_length=None)
            dataframe.write_parquet(dataframe_buffer)
            write_key = f"aemo/gas/vichub/{name.split('.')[0]}.parquet"
            _ = dataframe_buffer.seek(0)
            s3_client.upload_fileobj(dataframe_buffer, LANDING_BUCKET, write_key)

    # this object is a zip object of csv's

    context.log.info("finished extracting files and uploading to s3")

    target_file = f"s3://{LANDING_BUCKET}/{key}"

    delta_table = DeltaTable(delta_table_path)

    _ = delta_table.update(
        predicate=f"target_file = '{target_file}'",
        updates={
            "processed_datetime": dt.datetime.now().strftime(
                "TO_TIMESTAMP('%Y-%m-%d %H:%M:%S')"
            )
        },
    )

    _ = s3_client.delete_object(Bucket=LANDING_BUCKET, Key=key)

    context.log.info(f"finished processing csv file {LANDING_BUCKET}/{key}")


@dg.graph
def process_zip_files_op():
    def _process_zip_op(key: str) -> None:
        process_zip_op(key)

    create_dynamic_process_zip_op().map(_process_zip_op)

import datetime as dt
import io
import zipfile
from collections.abc import Generator
from dataclasses import dataclass
from io import BytesIO

import dagster as dg
import polars as pl
import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement
from dagster_aws.s3 import S3Resource
from types_boto3_s3.client import S3Client

from aemo_gas.vichub.assets.bronze.table_locations import (
    register as table_locations_register,
)
from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET
from aemo_gas import utils
from aemo_gas.vichub import ops

schema = dict(
    source_file=pl.String,
    target_file=pl.String,
    upload_datetime=pl.Datetime,
    ingested_datetime=pl.Datetime,
)


@dataclass
class Link:
    target_filename: str
    href: str
    upload_datetime: dt.datetime


@dataclass
class ProcessedLink:
    source_file: str
    target_file: str
    upload_datetime: dt.datetime
    ingested_datetime: dt.datetime


table_name = "downloaded_public_files"
table_s3_location = f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/{table_name}"


table_locations_register[table_name] = table_s3_location

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                               op to get all VicGas links                               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    name="get_links",
    description="extract all the links from https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/",
)
def get_links_op(context: dg.OpExecutionContext) -> list[Link]:
    root_url = "https://www.nemweb.com.au"

    vic_gas_folder = f"{root_url}/REPORTS/CURRENT/VicGas/"

    root_page = requests.get(vic_gas_folder)

    context.log.info(f"getting links from the {vic_gas_folder}")

    assert root_page.status_code == 200, f"request failed: {root_page.text}"

    root_soup = BeautifulSoup(root_page.text, features="html.parser")

    links: list[Link] = []

    tag: PageElement
    for tag in root_soup.find_all("a"):
        if "To Parent Directory" not in tag.get_text():
            target_filename = tag.get_text()
            href: str = f"{root_url}/{tag.get('href').lstrip('/')}"  # pyright: ignore[reportAttributeAccessIssue,reportOptionalMemberAccess]

            context.log.info(f"found link {href}")

            previous_element = tag.previous_element
            if isinstance(previous_element, str):
                datetime_string = " ".join(previous_element.split()[:-1])
            else:
                raise TypeError(f"No upload time found for {href}")
            upload_datetime = dt.datetime.strptime(
                datetime_string, "%A, %B %d, %Y %I:%M %p"
            )

            if "CURRENTDAY" not in href:
                links.append(
                    Link(
                        target_filename=target_filename,
                        href=href,
                        upload_datetime=upload_datetime,
                    )
                )
            else:
                context.log.info("Ignoring Current Day File")

            context.log.info(f"found link {href}")

            assert target_filename is not None

    # for each link also include date creation datetime

    for link in links:
        name, suffix = link.target_filename.split(".")
        link.target_filename = (
            f"{name}~{link.upload_datetime.strftime('%Y%m%d%H%M%S')}.{suffix}"
        )

    context.log.info(f"finished getting links from the {vic_gas_folder}")

    return links


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                           create the dynamic download groups                           │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(out=dg.DynamicOut())
def create_dynamic_download_group_op(
    context: dg.OpExecutionContext,
    links: list[Link],
    current_downloaded_files_df: pl.LazyFrame | None,
) -> Generator[dg.DynamicOutput[Link]]:
    context.log.info("creating dynamic download group")
    filtered_links: list[Link] = []
    # let's filter out the links
    for link in links:
        # check if the file has already been downloaded, if it has then skip
        if current_downloaded_files_df is not None:
            sub_df = current_downloaded_files_df.filter(
                pl.col("source_file") == link.href,
                pl.col("upload_datetime") == link.upload_datetime,
            )
            if sub_df.select(pl.len()).collect().item() == 0:
                context.log.info(f"kept link {link.href}")
                filtered_links.append(link)
        else:
            context.log.info(f"kept link {link.href}")
            filtered_links.append(link)

    # now pump out the values
    for idx, link in enumerate(filtered_links):
        yield dg.DynamicOutput[Link](
            link,
            mapping_key=f"link_{idx}",
        )

    context.log.info("finished creating dynamic download group")


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                               function to process links                                │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    retry_policy=dg.RetryPolicy(
        max_retries=3,
        delay=0.2,  # 200ms
        backoff=dg.Backoff.EXPONENTIAL,
        jitter=dg.Jitter.PLUS_MINUS,
    )
)
def process_link_op(
    context: dg.OpExecutionContext,
    s3_resource: S3Resource,
    link: Link,
) -> ProcessedLink | None:
    s3_client: S3Client = s3_resource.get_client()

    context.log.info(f"processing {link.href}")
    response = requests.get(link.href)

    assert response.status_code == 200, f"request failed: {response.text}"

    buffer = BytesIO(response.content)

    # ── convert the file to a parquet when possible ─────────────────────────────────

    extension = link.target_filename.lower().split(".")[-1]
    if extension == "csv":
        upload_filename = link.target_filename.lower().replace(".csv", ".parquet")
        csv_df = pl.read_csv(buffer, infer_schema_length=None)
        buffer = BytesIO()
        csv_df.write_parquet(buffer)
    else:
        upload_filename = link.target_filename

    _ = buffer.seek(0)

    s3_client.upload_fileobj(
        buffer,
        LANDING_BUCKET,
        f"aemo/gas/vichub/{upload_filename}",
    )

    processed_link = ProcessedLink(
        source_file=link.href,
        target_file=f"s3://{LANDING_BUCKET}/aemo/gas/vichub/{upload_filename}",
        upload_datetime=link.upload_datetime,
        ingested_datetime=dt.datetime.now(),
    )

    context.log.info(
        f"finished processing and uploading {link.href} to s3://{LANDING_BUCKET}/aemo/gas/vichub/{upload_filename}"
    )
    return processed_link


def _process_link_wrapper(link: Link) -> ProcessedLink | None:
    processed: ProcessedLink | None = process_link_op(link)
    return processed


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                combine into a dataframe                                │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op()
def combine_to_dataframe_op(
    context: dg.OpExecutionContext, processed_links: list[ProcessedLink | None]
) -> pl.LazyFrame:
    context.log.info("combining links into dataframe")
    filtered_links: list[ProcessedLink] = [
        link for link in processed_links if link is not None
    ]

    output = pl.LazyFrame(
        dict(
            source_file=[link.source_file for link in filtered_links],
            target_file=[link.target_file for link in filtered_links],
            upload_datetime=[link.upload_datetime for link in filtered_links],
            ingested_datetime=[link.ingested_datetime for link in filtered_links],
        ),
        schema=schema,
    )

    context.log.info("finished combining links into dataframe")

    return output


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      create a dynamic process to unzip the files                       │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    out=dg.DynamicOut(),
    ins={"processed_links": dg.In(dg.Nothing)},
)
def create_dynamic_process_uzip_op(
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


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                               for each zip file unzip it                               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    retry_policy=dg.RetryPolicy(
        max_retries=10,
        delay=1,  # 1s
        backoff=dg.Backoff.EXPONENTIAL,
        jitter=dg.Jitter.PLUS_MINUS,
    )
)
def process_unzip_op(
    context: dg.OpExecutionContext, s3_resource: S3Resource, key: str
) -> list[dict[str, str]]:
    context.log.info(f"processing zip file s3://{LANDING_BUCKET}/{key}")
    s3_client: S3Client = s3_resource.get_client()
    response = s3_client.get_object(Bucket=LANDING_BUCKET, Key=key)
    zip_io = io.BytesIO(response["Body"].read())
    unzipped_files: list[dict[str, str]] = []
    with zipfile.ZipFile(zip_io) as f:
        for name in f.namelist():
            buffer = io.BytesIO(f.read(name))

            # ── convert the file to a parquet when possible ─────────────────────────────────
            extension = name.lower().split(".")[-1]
            if extension == "csv":
                name = name.lower().replace(".csv", ".parquet")
                csv_df = pl.read_csv(buffer, infer_schema_length=None)
                buffer = BytesIO()
                csv_df.write_parquet(buffer)

            write_key = f"aemo/gas/vichub/{name}"

            _ = buffer.seek(0)

            s3_client.upload_fileobj(buffer, LANDING_BUCKET, write_key)
            unzipped_files.append({"Bucket": LANDING_BUCKET, "Key": write_key})
    response = s3_client.delete_object(Bucket=LANDING_BUCKET, Key=key)
    context.log.info(
        f"processed and finished cleanup for zip file s3://{LANDING_BUCKET}/{key} with response {response}"
    )
    return unzipped_files


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                             create a final passthrough op                              │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    ins={
        "start": dg.In(dg.Nothing),
    },
    out=dg.Out(
        io_manager_key="bronze_aemo_gas_deltalake_upsert_io_manager",
        metadata={
            "merge_predicate": utils.join_by_newlines(
                "s.source_file = t.source_file",
                "and s.target_file = t.target_file",
            ),
            "schema": "vichub",
        },
    ),
)
def final_passthrough(
    context: dg.AssetExecutionContext,
    output_df: pl.LazyFrame,
) -> pl.LazyFrame:
    context.log.info(f"adding preview: {table_s3_location}")

    metadata = {}

    df_preview = utils.get_table(table_s3_location)

    if df_preview is None:
        df_preview = output_df
        context.log.info(
            f"{table_s3_location} not found, previewing using upserted rows"
        )

    metadata["preview"] = dg.MetadataValue.md(
        df_preview.head().collect().to_pandas().to_markdown()
    )

    context.add_output_metadata(metadata)
    return output_df


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                   generate the required asset from the graph of ops                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.graph_asset(
    group_name="BRONZE__AEMO__GAS__VICHUB",
    key_prefix=["bronze", "aemo", "gas", "vichub"],
    name=table_name,
    description="Table listing public files downloaded from https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/ and converted to parquet",
    kinds={"deltalake", "table", "source"},
)
def asset() -> pl.LazyFrame:
    def unzip_wrapper(key: str) -> list[dict[str, str]]:
        return process_unzip_op(key)

    links: list[Link] = get_links_op()

    # get the downloaded_public_files df
    current_downloaded_public_files = ops.tables.get_downloaded_public_files()

    # filter out the links using the current downloaded files and download them all in parallel
    processed_links = (
        create_dynamic_download_group_op(links, current_downloaded_public_files)
        .map(_process_link_wrapper)
        .collect()
    )

    # unzip all the files which have been downloaded
    unzipped_files = (
        create_dynamic_process_uzip_op(processed_links=processed_links)
        .map(unzip_wrapper)
        .collect()
    )

    # combine the links into a dataframe
    df = combine_to_dataframe_op(processed_links)

    output_df = final_passthrough(df, start=unzipped_files)

    return output_df

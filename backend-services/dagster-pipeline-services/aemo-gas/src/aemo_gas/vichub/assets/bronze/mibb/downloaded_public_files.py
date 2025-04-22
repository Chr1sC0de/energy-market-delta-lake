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

from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET
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


delta_table_path = f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/downloaded_public_files/"

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                               op to get all VicGas links                               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    name="aemo_gas_vichub_get_links",
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
def aemo_gas_vichub_create_dynamic_download_group_op(
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
def aemo_gas_vichub_process_link_op(
    context: dg.OpExecutionContext, link: Link, s3_resource: S3Resource
) -> ProcessedLink | None:
    s3_client: S3Client = s3_resource.get_client()

    context.log.info(f"processing {link.href}")
    context.log.info(f"downloading {link.href}")
    response = requests.get(link.href)

    assert response.status_code == 200, f"request failed: {response.text}"

    context.log.info(f"finished downloading {link.href}")

    if link.href.lower().endswith(".csv"):
        buffer = BytesIO()
        pl.read_csv(response.content, infer_schema_length=None).write_parquet(buffer)
        link.target_filename = link.target_filename.lower().replace(".csv", ".parquet")
    else:
        buffer = BytesIO(response.content)

    context.log.info(
        f"uploading {link.href} to s3://{LANDING_BUCKET}/aemo/gas/vichub/{link.target_filename}"
    )

    _ = buffer.seek(0)

    s3_client.upload_fileobj(
        buffer,
        LANDING_BUCKET,
        f"aemo/gas/vichub/{link.target_filename}",
    )

    processed_link = ProcessedLink(
        source_file=link.href,
        target_file=f"s3://{LANDING_BUCKET}/aemo/gas/vichub/{link.target_filename}",
        upload_datetime=link.upload_datetime,
        ingested_datetime=dt.datetime.now(),
    )

    context.log.info(f"finished processing {link.href}")
    return processed_link


def _process_link_wrapper(link: Link) -> ProcessedLink | None:
    processed: ProcessedLink | None = aemo_gas_vichub_process_link_op(link)
    return processed


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                combine into a dataframe                                │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op()
def aemo_gas_vichub_combine_to_dataframe_op(
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
def aemo_gas_vichub_create_dynamic_process_uzip_op(
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
def aemo_gas_vichub_process_unzip_op(
    context: dg.OpExecutionContext, s3_resource: S3Resource, key: str
) -> str:
    context.log.info(f"processing zip file s3://{LANDING_BUCKET}/{key}")
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
    context.log.info("finished extracting files and uploading to s3")
    context.log.info(f"deleting s3://{LANDING_BUCKET}/{key}")
    response = s3_client.delete_object(Bucket=LANDING_BUCKET, Key=key)
    context.log.info(
        f"finished deleting object s3://{LANDING_BUCKET}/{key} with response {response}"
    )
    return key


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
def aemo_gas_vichub_final_passthrough(
    context: dg.AssetExecutionContext,
    output_df: pl.LazyFrame,
) -> pl.LazyFrame:
    context.log.info(
        f"adding preview: {BRONZE_AEMO_GAS_DIRECTORY}/vichub/bronze_aemo_gas_deltalake_upsert_io_manager"
    )

    metadata = {}

    df_preview = utils.get_table(
        f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/bronze_aemo_gas_deltalake_upsert_io_manager"
    )

    if df_preview is None:
        df_preview = output_df
        context.log.info(
            f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/bronze_aemo_gas_deltalake_upsert_io_manager not found, previewing using upserted rows"
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
    name="downloaded_public_files",
    description="Table listing public files downloaded from https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/ and converted to parquet",
    kinds={"deltalake", "source"},
)
def asset() -> pl.LazyFrame:
    def unzip_wrapper(key: str) -> str:
        return aemo_gas_vichub_process_unzip_op(key)

    links: list[Link] = get_links_op()

    # get the downloaded_public_files df
    current_downloaded_public_files = ops.get_table_op.factory(
        "aemo_vichub_gas_downloaded_public_files", delta_table_path
    )()

    # filter out the links using the current downloaded files and download them all in parallel
    processed_links = (
        aemo_gas_vichub_create_dynamic_download_group_op(
            links, current_downloaded_public_files
        )
        .map(_process_link_wrapper)
        .collect()
    )

    # unzip all the files which have been downloaded
    unzipped_files = (
        aemo_gas_vichub_create_dynamic_process_uzip_op(processed_links=processed_links)
        .map(unzip_wrapper)
        .collect()
    )

    # combine the links into a dataframe
    df = aemo_gas_vichub_combine_to_dataframe_op(processed_links)

    output_df = aemo_gas_vichub_final_passthrough(df, start=unzipped_files)

    return output_df

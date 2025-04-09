import datetime as dt
from collections.abc import Generator
from dataclasses import dataclass
from io import BytesIO
from logging import Logger

import dagster as dg
import polars as pl
import requests
from bs4 import BeautifulSoup
from bs4.element import PageElement
from dagster_aws.s3 import S3Resource
from deltalake.exceptions import TableNotFoundError
from types_boto3_s3.client import S3Client
from deltalake import DeltaTable

from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET
from aemo_gas.utils import join_by_newlines


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
    processed_datetime: dt.datetime | None


delta_table_path = f"{BRONZE_AEMO_GAS_DIRECTORY}/vichub/downloaded_files_metadata/"

# op to get all VicGas links


def get_links(logger: Logger | None = None) -> list[Link]:
    # set root url and create the soup
    root_url = "https://www.nemweb.com.au"

    root_page = requests.get(f"{root_url}/REPORTS/CURRENT/VicGas/")

    assert root_page.status_code == 200, f"request failed: {root_page.text}"

    root_soup = BeautifulSoup(root_page.text, features="html.parser")

    # grab all the links

    links: list[Link] = []

    tag: PageElement
    for tag in root_soup.find_all("a"):
        if "To Parent Directory" not in tag.get_text():
            target_filename = tag.get_text()
            href: str = f"{root_url}/{tag.get('href').lstrip('/')}"  # pyright: ignore[reportAttributeAccessIssue,reportOptionalMemberAccess]
            previous_element = tag.previous_element
            if isinstance(previous_element, str):
                datetime_string = " ".join(previous_element.split()[:-1])
            else:
                raise TypeError(f"No upload time found for {href}")
            upload_datetime = dt.datetime.strptime(
                datetime_string, "%A, %B %d, %Y %I:%M %p"
            )

            links.append(
                Link(
                    target_filename=target_filename,
                    href=href,
                    upload_datetime=upload_datetime,
                )
            )

            if logger is not None:
                logger.info(f"found link {href}")

            assert target_filename is not None

    # for each link also include date creation datetime

    for link in links:
        name, suffix = link.target_filename.split(".")
        link.target_filename = (
            f"{name}~{link.upload_datetime.strftime('%y%m%d%H%M%S')}.{suffix}"
        )
    return links


@dg.op()
def get_links_op(context: dg.OpExecutionContext) -> list[Link]:
    return get_links(context.log)


# get the current metadata df


def get_current_download_file_metadata_df() -> pl.DataFrame | None:
    try:
        df = pl.read_delta(delta_table_path)
    except TableNotFoundError:
        df = None
    return df


@dg.op()
def get_current_download_file_metadata_df_op() -> pl.DataFrame | None:
    return get_current_download_file_metadata_df()


# create the dynamic download groups


@dg.op(out=dg.DynamicOut())
def create_dynamic_download_group_op(
    context: dg.OpExecutionContext,
    links: list[Link],
    current_download_file_metadata_df: pl.DataFrame | None,
) -> Generator[dg.DynamicOutput[Link]]:
    filtered_links: list[Link] = []
    # let's filter out the links
    for link in links:
        # check if the file has already been downloaded, if it has then skip
        if current_download_file_metadata_df is not None:
            sub_df = current_download_file_metadata_df.filter(
                pl.col("source_file") == link.href,
                pl.col("upload_datetime") == link.upload_datetime,
            )
            if len(sub_df) == 0:
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


# function to process links


@dg.op(
    retry_policy=dg.RetryPolicy(
        max_retries=3,
        delay=0.2,  # 200ms
        backoff=dg.Backoff.EXPONENTIAL,
        jitter=dg.Jitter.PLUS_MINUS,
    )
)
def process_link_op(
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
        processed_datetime=None,
    )

    context.log.info(f"finished processing {link.href}")
    return processed_link


def _process_link(link: Link) -> ProcessedLink | None:
    processed: ProcessedLink | None = process_link_op(link)
    return processed


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                  filter out the nones                                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op()
def filter_none_op(processed_links: list[ProcessedLink | None]) -> list[ProcessedLink]:
    return [link for link in processed_links if link is not None]


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                combine into a dataframe                                │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.op(
    out=dg.Out(
        io_manager_key="bronze_aemo_gas_upsert_io_manager",
        metadata={
            "merge_predicate": join_by_newlines(
                "s.source_file = t.source_file",
                "and s.target_file = t.target_file",
            ),
        },
    )
)
def combine_to_dataframe_op(
    context: dg.OpExecutionContext, processed_links: list[ProcessedLink]
) -> pl.LazyFrame:
    schema = dict(
        source_file=str,
        target_file=str,
        upload_datetime=dt.datetime,
        ingested_datetime=dt.datetime,
        processed_datetime=dt.datetime,
    )
    output = pl.LazyFrame(
        dict(
            source_file=[link.source_file for link in processed_links],
            target_file=[link.target_file for link in processed_links],
            upload_datetime=[link.upload_datetime for link in processed_links],
            ingested_datetime=[link.ingested_datetime for link in processed_links],
            processed_datetime=[None] * len(processed_links),
        ),
        schema=schema,
    )

    retention_hours = 7

    metadata: dict[str, dg.MetadataValue] = {}

    markdown_table = output.collect().to_pandas().to_markdown()

    if markdown_table is not None:
        metadata["upserted rows"] = dg.MetadataValue.md(markdown_table)

    metadata["retention hours"] = dg.MetadataValue.int(retention_hours)

    context.add_output_metadata(metadata)

    try:
        context.log.info(
            f"Vacuumed:\n{DeltaTable(delta_table_path).vacuum(retention_hours=retention_hours, enforce_retention_duration=False, dry_run=False)}"
        )
    except TableNotFoundError:
        pass

    return output


# generate the required asset


@dg.graph_asset(
    key_prefix=["vichub"],
    group_name="BRONZE__AEMO__VICHUB",
    kinds={"deltalake"},
)
def downloaded_files_metadata() -> pl.LazyFrame:
    links: list[Link] = get_links_op()

    current_download_file_metadata_df: pl.DataFrame | None = (
        get_current_download_file_metadata_df_op()
    )

    processed_links = create_dynamic_download_group_op(
        links, current_download_file_metadata_df
    ).map(_process_link)

    filtered_processed_links = filter_none_op(processed_links.collect())

    output_df: pl.LazyFrame = combine_to_dataframe_op(filtered_processed_links)

    return output_df


@dg.asset_check(asset=downloaded_files_metadata)
def has_no_duplicate_source_and_target_entries(
    downloaded_files_metadata: pl.LazyFrame,
):
    # Return the result of the check
    return dg.AssetCheckResult(
        # Define passing criteria
        passed=bool(
            downloaded_files_metadata.select(pl.len()).collect().item()
            == downloaded_files_metadata.select("source_file", "target_file")
            .unique()
            .select(pl.len())
            .collect()
            .item()
        ),
    )


assets = [downloaded_files_metadata]
checks = [has_no_duplicate_source_and_target_entries]

from typing import Unpack, cast

from dagster import Any, AssetsDefinition, MetadataValue, graph_asset
from polars import Datetime, LazyFrame, Schema, String

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    DynamicNEMWebLinksFetcher,
    build_dynamic_nemweb_links_fetcher_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    DynamicZipLinksFetcher,
    build_dynamic_zip_link_fetcher_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.file_unzipper import (
    FileUnzipper,
    build_unzip_files_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_fetcher import (
    NEMWebLinkFetcher,
    build_nemweb_link_fetcher_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_processor import (
    S3NemwebLinkProcessor,
    build_nemweb_link_processor_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.processed_link_combiner import (
    ProcessedLinkedCombiner,
    build_process_link_combiner_op,
)
from aemo_etl.models import GraphAssetKwargs
from aemo_etl.utils import get_metadata_schema

SURROGATE_KEY_SOURCES = [
    "source_absolute_href",
    "source_upload_datetime",
    "target_s3_name",
    "target_ingested_datetime",
]

SCHEMA = Schema(
    {
        "source_absolute_href": String,
        "source_upload_datetime": Datetime("ms", time_zone="UTC"),
        "target_s3_href": String,
        "target_s3_bucket": String,
        "target_s3_prefix": String,
        "target_s3_name": String,
        "target_ingested_datetime": Datetime("ms", time_zone="UTC"),
        "surrogate_key": String,
    }
)

DESCRIPTIONS = {
    "source_absolute_href": "Full link to the source file",
    "source_upload_datetime": """
        Time the data was uploaded onto the website in Australia/Melbourne time zone
    """,
    "target_s3_href": """
        The s3 bucket the file is stored in, if the file can be converted to a
        parquet it will be converted to a parquet
    """,
    "target_s3_bucket": "The name of the bucket the file will be saved in",
    "target_s3_prefix": "The s3 prefix",
    "target_s3_name": "The name of the file saved",
    "target_ingested_datetime": """
        The datetime the file was ingested in Australia/Melbourne time zone
    """,
    "surrogate_key": f"surrogate key created from columns {SURROGATE_KEY_SOURCES}",
}

assert len(SCHEMA) == len(DESCRIPTIONS)


def nemweb_public_files_asset_factory(
    *,
    name: str,
    nemweb_relative_href: str,
    s3_landing_prefix: str,
    nemweb_link_fetcher: NEMWebLinkFetcher,
    dynamic_nemweb_links_fetcher: DynamicNEMWebLinksFetcher,
    nemweb_link_processor: S3NemwebLinkProcessor,
    dynamic_zip_link_fetcher: DynamicZipLinksFetcher,
    file_unzipper: FileUnzipper,
    processed_link_combiner: ProcessedLinkedCombiner,
    s3_landing_bucket: str = LANDING_BUCKET,
    io_manager_key: str | None = None,
    out_metadata_kwargs: dict[str, Any] | None = None,
    **graph_asset_kwargs: Unpack[GraphAssetKwargs],
) -> AssetsDefinition:

    out_metadata_kwargs = out_metadata_kwargs or {}
    graph_asset_kwargs = graph_asset_kwargs or {}
    graph_asset_kwargs.setdefault("group_name", "AEMO")
    graph_asset_kwargs.setdefault(
        "description",
        f"""
            Table listing public files downloaded from https://www.nemweb.com.au/{nemweb_relative_href}
            and converted to parquet where possible.
        """,
    )

    graph_asset_kwargs.setdefault("kinds", {"source", "table", "deltalake"})

    if "dagster/column_schema" not in out_metadata_kwargs:
        out_metadata_kwargs["dagster/column_schema"] = get_metadata_schema(
            SCHEMA, DESCRIPTIONS
        )
        out_metadata_kwargs["surrogate_key_sources"] = MetadataValue.json(
            SURROGATE_KEY_SOURCES
        )

    nemweb_link_fetcher_op = build_nemweb_link_fetcher_op(
        name, nemweb_relative_href, nemweb_link_fetcher
    )
    dynamic_dynamic_nemweb_link_fetcher_op = build_dynamic_nemweb_links_fetcher_op(
        name, nemweb_relative_href, dynamic_nemweb_links_fetcher
    )
    nemweb_link_processor_op = build_nemweb_link_processor_op(
        name, s3_landing_bucket, s3_landing_prefix, nemweb_link_processor
    )
    dynamic_zip_link_fetcher_op = build_dynamic_zip_link_fetcher_op(
        name, s3_landing_bucket, s3_landing_prefix, dynamic_zip_link_fetcher
    )
    unzip_files_op = build_unzip_files_op(
        name, s3_landing_bucket, s3_landing_prefix, file_unzipper
    )
    processed_link_combiner_op = build_process_link_combiner_op(
        name,
        SCHEMA,
        SURROGATE_KEY_SOURCES,
        io_manager_key,
        out_metadata_kwargs,
        processed_link_combiner,
    )

    @graph_asset(name=name, **(graph_asset_kwargs or {}))
    def download_nemweb_public_files_to_s3_asset() -> LazyFrame:
        links = nemweb_link_fetcher_op()
        processed_links = (
            dynamic_dynamic_nemweb_link_fetcher_op(links)
            .map(nemweb_link_processor_op)
            .collect()
        )
        unzipped_files_log = (
            dynamic_zip_link_fetcher_op(start=processed_links)
            .map(unzip_files_op)
            .collect()
        )
        df = processed_link_combiner_op(processed_links, start=unzipped_files_log)
        return cast(LazyFrame, df)

    return download_nemweb_public_files_to_s3_asset

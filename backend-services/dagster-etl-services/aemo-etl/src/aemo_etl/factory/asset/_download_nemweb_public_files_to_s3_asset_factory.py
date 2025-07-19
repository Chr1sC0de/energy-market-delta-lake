from io import BytesIO
from typing import Any, Callable, Unpack

from dagster import (
    In,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    Out,
    graph_asset,
    op,
)
from polars import Datetime, LazyFrame, String

from aemo_etl.configuration import LANDING_BUCKET, Link
from aemo_etl.factory.asset.param_spec import GraphAssetParamSpec
from aemo_etl.factory.op import (
    combine_processed_links_to_dataframe_op_factory,
    download_link_and_upload_to_s3_op_factory,
    get_dynamic_nemweb_links_op_factory,
    get_nemweb_links_op_factory,
    unzip_s3_file_from_key_op_factory,
)
from aemo_etl.factory.op._get_dynamic_zip_links_op_factory import (
    get_dyanmic_zip_links_op_factory,
)
from aemo_etl.util import get_metadata_schema


def download_nemweb_public_files_to_s3_asset_factory(
    *,
    nemweb_relative_href: str,
    s3_source_prefix: str,
    s3_source_bucket: str = LANDING_BUCKET,
    out_metadata: dict[Any, Any] | None = None,
    io_manager_key: str | None = None,
    link_filter: Callable[[OpExecutionContext, Link], bool] | None = None,
    get_buffer_from_link_hook: Callable[[Link], BytesIO] | None = None,
    override_get_links_fn: Callable[[OpExecutionContext], list[Link]] | None = None,
    **graph_asset_kwargs: Unpack[GraphAssetParamSpec],
):
    name = graph_asset_kwargs.get("name")
    graph_asset_kwargs.setdefault("group_name", "AEMO")
    graph_asset_kwargs.setdefault(
        "description",
        f"Table listing public files downloaded from https://www.nemweb.com.au/{nemweb_relative_href} and converted to parquet where possible",
    )
    graph_asset_kwargs.setdefault("kinds", {"source", "table", "deltalake"})

    schema = {
        "source_absolute_href": String,
        "source_upload_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
        "target_s3_href": String,
        "target_s3_bucket": String,
        "target_s3_prefix": String,
        "target_s3_name": String,
        "target_ingested_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
    }

    descriptions = {
        "source_absolute_href": "Full link to the source file",
        "source_upload_datetime": "Time the data was uploaded onto the website in Australia/Melbourne time zone",
        "target_s3_href": "The s3 bucket the file is stored in, if the file can be converted to a parquet it will be converted to a parquet",
        "target_s3_bucket": "The name of the bucket the file will be saved in",
        "target_s3_prefix": "The s3 prefix",
        "target_s3_name": "The name of the file saved",
        "target_ingested_datetime": "The datetime the file was ingested in Australia/Melbourne time zone",
    }

    if out_metadata is not None:
        if "dagster/column_schema" not in out_metadata:
            out_metadata["dagster/column_schema"] = get_metadata_schema(
                schema, descriptions
            )

    def final_passthrough_op_factory() -> OpDefinition:
        @op(
            name=f"{name}_final_passthrough_op",
            ins={
                "start": In(Nothing),
            },
            out=Out(
                io_manager_key=io_manager_key,
                metadata=out_metadata,
            ),
        )
        def final_passthrough_op(
            output_df: LazyFrame,
        ) -> LazyFrame:
            return output_df

        return final_passthrough_op

    @graph_asset(**graph_asset_kwargs)
    def download_nemweb_public_files_to_s3_asset() -> LazyFrame:
        links = get_nemweb_links_op_factory(
            name=f"{name}_get_nemweb_links_op",
            relative_root_href=nemweb_relative_href,
            override_get_links_fn=override_get_links_fn,
            description=f"extract the list of links from {nemweb_relative_href}",
        )()

        processed_links = (
            get_dynamic_nemweb_links_op_factory(
                name=f"{name}_get_dynamic_nemweb_links_op",
                link_filter=link_filter,
                description="create a dynamic set of links and process them",
            )(links)
            .map(
                lambda link: download_link_and_upload_to_s3_op_factory(
                    name=f"{name}_download_link_and_upload_to_s3_op",
                    description=f"download file from a link and upload into s3://{s3_source_bucket}/{s3_source_prefix}",
                    s3_landing_bucket=s3_source_bucket,
                    s3_landing_prefix=s3_source_prefix,
                    get_buffer_from_link_hook=get_buffer_from_link_hook,
                )(link)
            )
            .collect()
        )

        unzipped_s3_files_log = (
            get_dyanmic_zip_links_op_factory(
                name=f"{name}_get_dyanmic_zip_links_op",
                description="create a dynamic list of keys for a bucket",
                s3_source_bucket=s3_source_bucket,
                s3_source_prefix=s3_source_prefix,
            )(start=processed_links)
            .map(
                lambda keys: unzip_s3_file_from_key_op_factory(
                    name=f"{name}_unzip_s3_file_from_key_op",
                    description=f"unzip files and load the content into s3://{s3_source_bucket}/{s3_source_prefix}",
                    s3_source_bucket=s3_source_bucket,
                    s3_target_bucket=s3_source_bucket,
                    s3_target_prefix=s3_source_prefix,
                )(keys)
            )
            .collect()
        )

        df = combine_processed_links_to_dataframe_op_factory(
            name=f"{name}_combine_processed_links_to_dataframe_op",
            schema=schema,
            description="for each processed link, combine the downloaded files into a single data frame",
        )(processed_links)

        return final_passthrough_op_factory()(df, start=unzipped_s3_files_log)

    return download_nemweb_public_files_to_s3_asset

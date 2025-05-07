from io import BytesIO
from typing import Callable, Unpack

from dagster import (
    In,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    Out,
    graph_asset,
    op,
)
from polars import LazyFrame

from aemo_etl.configuration import LANDING_BUCKET, Link
from aemo_etl.factory.asset.schema import MandatedGraphAssetKwargs
from aemo_etl.factory.op import (
    combine_processed_links_to_dataframe_op_factory,
    download_link_and_upload_to_s3_op_factory,
    get_dynamic_nemweb_links_op_factory,
)
from aemo_etl.factory.op._get_dynamic_zip_links_op_factory import (
    get_dyanmic_zip_links_op_factory,
)
from aemo_etl.factory.op import get_nemweb_links_op_factory
from aemo_etl.factory.op import (
    unzip_s3_file_from_key_op_factory,
)


def download_nemweb_public_files_to_s3_asset_factory(
    *,
    io_manager_key: str | None = None,
    s3_source_prefix: str,
    s3_source_bucket: str = LANDING_BUCKET,
    nemweb_relative_href: str,
    out_metadata: dict[str, str] | None = None,
    link_filter: Callable[[OpExecutionContext, Link], bool] | None = None,
    get_buffer_from_link_hook: Callable[[Link], BytesIO] | None = None,
    post_process_hook: Callable[[OpExecutionContext, LazyFrame], LazyFrame]
    | None = None,
    override_get_links_fn: Callable[[OpExecutionContext], list[Link]] | None = None,
    **graph_asset_kwargs: Unpack[MandatedGraphAssetKwargs],
):
    graph_asset_kwargs.setdefault("group_name", "AEMO")
    graph_asset_kwargs.setdefault(
        "description",
        f"Table listing public files downloaded from https://www.nemweb.com.au/{nemweb_relative_href} and converted to parquet where possible",
    )
    graph_asset_kwargs.setdefault("kinds", {"source", "table", "deltalake"})

    def final_passthrough_op_factory() -> OpDefinition:
        @op(
            ins={
                "start": In(Nothing),
            },
            out=Out(
                io_manager_key=io_manager_key,
                metadata=out_metadata,
            ),
        )
        def final_passthrough_op(
            context: OpExecutionContext,
            output_df: LazyFrame,
        ) -> LazyFrame:
            if post_process_hook is not None:
                post_process_hook(context, output_df)

            return output_df

        return final_passthrough_op

    @graph_asset(**graph_asset_kwargs)
    def download_nemweb_public_files_to_s3_asset() -> LazyFrame:
        links = get_nemweb_links_op_factory(
            relative_root_href=nemweb_relative_href,
            override_get_links_fn=override_get_links_fn,
            description=f"extract the list of links from {nemweb_relative_href}",
        )()

        processed_links = (
            get_dynamic_nemweb_links_op_factory(
                link_filter=link_filter,
                description="create a dynamic set of links and process them",
            )(links)
            .map(
                lambda link: download_link_and_upload_to_s3_op_factory(
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
                description="create a dynamic list of keys for a bucket",
                s3_source_bucket=s3_source_bucket,
                s3_source_prefix=s3_source_prefix,
            )(start=processed_links)
            .map(
                lambda keys: unzip_s3_file_from_key_op_factory(
                    description=f"unzip files and load the content into s3://{s3_source_bucket}/{s3_source_prefix}",
                    s3_source_bucket=s3_source_bucket,
                    s3_target_bucket=s3_source_bucket,
                    s3_target_prefix=s3_source_prefix,
                )(keys)
            )
            .collect()
        )

        df = combine_processed_links_to_dataframe_op_factory(
            description="for each processed link, combine the downloaded files into a single data frame",
        )(processed_links)

        return final_passthrough_op_factory()(df, start=unzipped_s3_files_log)

    return download_nemweb_public_files_to_s3_asset

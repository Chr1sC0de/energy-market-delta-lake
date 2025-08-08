from pathlib import Path
from typing import cast, override

from dagster import InputContext, IOManager, MetadataValue, OutputContext
from deltalake.exceptions import TableNotFoundError
from deltalake.table import TableMerger
from polars import LazyFrame, len as len_, scan_delta

from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
)
from aemo_etl.util import get_metadata_schema


class S3PolarsDeltaLakeIOManager(IOManager):
    """
    to pass configurations into io manager ensure `s3_polars_deltalake_io_manager_options`
    is mset in the metadata. The s3_polars_deltalake_io_manager_options should consist of
    an PolarsDataFrameWriteDeltaParamSpec and PolarsDataFrameReadDeltaParamSpec object e.g.

            metadata={
                "s3_polars_deltalake_io_manager_options": {
                    "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                        target=f"{s3_target_table}"
                    ),
                    "scan_delta_options": PolarsDataFrameReadDeltaParamSpec(
                        source=f"{s3_target_table}"
                    ),
                    "preview_row_count": 5
                }
            }
    """

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        definiton_metadata = context.definition_metadata
        assert definiton_metadata is not None, (
            "writing to s3 requires both write_delta_options and scan_delta_options to be set in asset metadata"
        )
        assert "s3_polars_deltalake_io_manager_options" in definiton_metadata, (
            "s3_polars_deltalake_io_manager_options must be set in asset metadata"
        )

        s3_polars_deltalake_io_manager_options = definiton_metadata[
            "s3_polars_deltalake_io_manager_options"
        ]

        assert f"write_delta_options in {s3_polars_deltalake_io_manager_options}"

        write_delta_options = s3_polars_deltalake_io_manager_options.get(
            "write_delta_options"
        )

        assert isinstance(write_delta_options, PolarsDataFrameWriteDeltaParamSpec), (
            "'write_delta_options' must be of type 'PolarsDataFrameWriteDeltaParamSpec'"
        )
        collected_obj = obj.collect()

        kwargs = write_delta_options.model_dump(by_alias=True)

        try:
            if len(collected_obj.columns) > 0:
                return_obj = collected_obj.write_delta(**kwargs)
                if kwargs.get("mode", "error") == "merge":
                    context.log.info(f"merging data with settings {kwargs}")
                    merge_results = (
                        cast(TableMerger, return_obj)
                        .when_matched_update_all()
                        .when_not_matched_insert_all()
                        .execute()
                    )
                    context.log.info(f"merged data with results {merge_results}")

        except TableNotFoundError:
            kwargs["mode"] = "error"
            context.log.info(kwargs)
            collected_obj.write_delta(**kwargs)

        context.add_output_metadata(
            {
                k: v
                for k, v in context.definition_metadata.items()
                if not k.endswith("io_manager_options")
            }
        )

        output_metadata = {}

        if isinstance(write_delta_options.target, str):
            output_metadata["table_uri"] = MetadataValue.path(
                write_delta_options.target
            )

        if isinstance(write_delta_options.target, Path):
            output_metadata["table_uri"] = MetadataValue.path(
                write_delta_options.target
            )

        scan_delta_options = s3_polars_deltalake_io_manager_options[
            "scan_delta_options"
        ]

        results_df = scan_delta(**scan_delta_options.model_dump(by_alias=True))

        markdown_preview = (
            results_df.head(
                s3_polars_deltalake_io_manager_options.get("preview_row_count", 5)
            )
            .collect()
            .to_pandas()
            .to_markdown()
        )

        if markdown_preview is not None:
            output_metadata["preview"] = MetadataValue.md(markdown_preview)

        output_metadata["dagster/row_count"] = MetadataValue.int(
            results_df.select(len_()).collect().item()
        )

        if "dagster/column_schema" not in context.definition_metadata:
            if "dagster/column_description" in context.definition_metadata:
                output_metadata["dagster/column_schema"] = get_metadata_schema(
                    results_df.collect_schema(),
                    context.definition_metadata["dagster/column_description"],
                )
            else:
                output_metadata["dagster/column_schema"] = get_metadata_schema(
                    results_df.collect_schema()
                )

        context.add_output_metadata(output_metadata)

    @override
    def load_input(self, context: InputContext) -> LazyFrame:
        assert context.upstream_output is not None, "upstream asset must not be null"

        definiton_metadata = context.upstream_output.definition_metadata

        assert definiton_metadata is not None, (
            "writing to s3 requires both write_delta_options and scan_delta_options to be set in asset metadata"
        )
        assert "s3_polars_deltalake_io_manager_options" in definiton_metadata, (
            "s3_polars_deltalake_io_manager_options must be set in asset metadata"
        )

        s3_polars_deltalake_io_manager_options = definiton_metadata[
            "s3_polars_deltalake_io_manager_options"
        ]

        assert f"scan_delta_options in {s3_polars_deltalake_io_manager_options}"

        scan_delta_options = s3_polars_deltalake_io_manager_options[
            "scan_delta_options"
        ]

        assert isinstance(scan_delta_options, PolarsDataFrameReadScanDeltaParamSpec), (
            "'scan_delta_options' must be of type 'PolarsDataFrameReadScanDeltaParamSpec'"
        )
        df = scan_delta(**scan_delta_options.model_dump(by_alias=True))
        return df

from typing import override

from dagster import InputContext, IOManager, MetadataValue, OutputContext
from polars import LazyFrame, len, scan_parquet
from polars._typing import PartitioningScheme

from aemo_etl.parameter_specification import (
    PolarsLazyFrameScanParquetParamSpec,
    PolarsLazyFrameSinkParquetParamSpec,
)
from aemo_etl.util import get_metadata_schema


class S3PolarsParquetIOManager(IOManager):
    """
    to pass configurations into io manager ensure `s3_polars_parquet_io_manager_options`
    is mset in the metadata. The s3_polars_parquet_io_manager_options should consist of
    an PolarsLazyFrameScanParquetParamSpec and PolarsLazyFrameSinkParquetParamSpec object e.g.

            metadata={
                "s3_polars_parquet_io_manager_options": {
                    "sink_parquet_options": PolarsLazyFrameSinkParquetParamSpec(
                        path=f"{s3_target_table}/result.parquet"
                    ),
                    "scan_parquet_options": PolarsLazyFrameScanParquetParamSpec(
                        source=f"{s3_target_table}/"
                    ),
                }
            }

    """

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        definiton_metadata = context.definition_metadata
        assert definiton_metadata is not None, (
            "writing to s3 requires both sink_parquet_options and scan_parquet_options to be set in asset metadata"
        )
        assert "s3_polars_parquet_io_manager_options" in definiton_metadata, (
            "s3_polars_parquet_io_manager_options must be set in asset metadata"
        )

        assert f"sink_parquet_options in {definiton_metadata['s3_polars_parquet_io_manager_options']}"

        sink_parquet_options = definiton_metadata[
            "s3_polars_parquet_io_manager_options"
        ].get("sink_parquet_options")

        assert isinstance(sink_parquet_options, PolarsLazyFrameSinkParquetParamSpec), (
            "'sink_parquet_options' must be of type 'PolarsLazyFrameSinkParquetParamSpec'"
        )
        obj.sink_parquet(**sink_parquet_options.model_dump(by_alias=True))
        context.add_output_metadata(
            {
                k: v
                for k, v in context.definition_metadata.items()
                if not k.endswith("io_manager_options")
            }
        )
        output_metadata = {}

        if isinstance(sink_parquet_options.path, str):
            output_metadata["table_uri"] = MetadataValue.path(sink_parquet_options.path)

        elif isinstance(sink_parquet_options.path, PartitioningScheme):
            if sink_parquet_options.path._base_path is not None:
                output_metadata["table_uri"] = MetadataValue.path(
                    sink_parquet_options.path._base_path
                )
        markdown_preview = obj.head().collect().to_pandas().to_markdown()

        if markdown_preview is not None:
            output_metadata["preview"] = MetadataValue.md(markdown_preview)

        output_metadata["dagster/row_count"] = MetadataValue.int(
            obj.select(len()).collect().item()
        )

        if "dagster/column_schema" not in context.definition_metadata:
            output_metadata["dagster/column_schema"] = get_metadata_schema(
                obj.collect_schema()
            )

        context.add_output_metadata(output_metadata)

    @override
    def load_input(self, context: InputContext) -> LazyFrame:
        assert context.upstream_output is not None, "upstream asset must not be null"

        definiton_metadata = context.upstream_output.definition_metadata

        assert definiton_metadata is not None, (
            "writing to s3 requires both sink_parquet_options and scan_parquet_options to be set in asset metadata"
        )
        assert "s3_polars_parquet_io_manager_options" in definiton_metadata, (
            "s3_polars_parquet_io_manager_options must be set in asset metadata"
        )

        assert f"scan_parquet_options in {definiton_metadata['s3_polars_parquet_io_manager_options']}"

        scan_parquet_options = definiton_metadata[
            "s3_polars_parquet_io_manager_options"
        ].get("scan_parquet_options")

        assert isinstance(scan_parquet_options, PolarsLazyFrameScanParquetParamSpec), (
            "'scan_parquet_options' must be of type 'PolarsLazyFrameScanParquetParamSpec'"
        )
        df = scan_parquet(**scan_parquet_options.model_dump(by_alias=True))
        return df

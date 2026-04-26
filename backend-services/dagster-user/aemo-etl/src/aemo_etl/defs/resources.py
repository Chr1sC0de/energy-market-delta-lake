from typing import override

from dagster import (
    Any,
    ConfigurableIOManager,
    Definitions,
    InputContext,
    MetadataValue,
    OutputContext,
    definitions,
)
from dagster._core.definitions.metadata import RawMetadataValue
from polars import LazyFrame, scan_delta, scan_parquet

from aemo_etl.configs import DAGSTER_URI
from aemo_etl.utils import get_lazyframe_num_rows, get_metadata_schema


class PolarsDataFrameSinkDeltaIoManager(ConfigurableIOManager):
    sink_delta_kwargs: dict[str, Any] = {}
    scan_delta_kwargs: dict[str, Any] = {}
    preview_row_count: int = 5

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        """automatically handles merges as upserts"""
        assert context.definition_metadata is not None, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.definition_metadata, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        target_uri = context.definition_metadata[DAGSTER_URI]

        markdown_preview = (
            obj.head(self.preview_row_count).collect().to_pandas().to_markdown()
        )
        output_metadata: dict[str, RawMetadataValue] = {}

        if "dagster/column_schema" not in context.definition_metadata:
            if "column_description" in context.definition_metadata:
                updated_column_schema = get_metadata_schema(
                    obj.collect_schema(),
                    context.definition_metadata["column_description"],
                )
            else:
                updated_column_schema = get_metadata_schema(obj.collect_schema())

            output_metadata["dagster/column_schema"] = updated_column_schema

        output_metadata.update(
            {
                "preview": MetadataValue.md(markdown_preview),
                "sink_delta_kwargs": MetadataValue.json(self.sink_delta_kwargs),
                "dagster/row_count": get_lazyframe_num_rows(obj),
            }
        )

        return_object = obj.sink_delta(target_uri, **self.sink_delta_kwargs)

        if self.sink_delta_kwargs.get("mode", "error") == "merge":
            assert return_object is not None, (
                "mode was set to merge but resulting output is None"
            )

            context.log.info(f"merging data with settings {self.sink_delta_kwargs}")

            merge_results = (
                return_object.when_matched_update_all()
                .when_not_matched_insert_all()
                .execute()
            )
            context.log.info(f"merged data with results {merge_results}")

        context.add_output_metadata(output_metadata)

    @override
    def load_input(self, context: InputContext) -> LazyFrame:
        assert context.upstream_output is not None, "echo no upstream output found"
        assert context.upstream_output.definition_metadata is not None, (
            f"upstream asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.upstream_output.definition_metadata, (
            f"upstream asset must set metadata {DAGSTER_URI}"
        )

        target_uri = context.upstream_output.definition_metadata[DAGSTER_URI]

        return scan_delta(target_uri, **self.scan_delta_kwargs)


def _parquet_dataset_glob(uri: str) -> str:
    return f"{uri.rstrip('/')}/*.parquet"


class PolarsDataFrameSinkParquetIoManager(ConfigurableIOManager):
    preview_row_count: int = 5

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        assert context.definition_metadata is not None, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.definition_metadata, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        target_uri = context.definition_metadata[DAGSTER_URI]

        markdown_preview = (
            obj.head(self.preview_row_count).collect().to_pandas().to_markdown()
        )
        output_metadata: dict[str, RawMetadataValue] = {}

        if "dagster/column_schema" not in context.definition_metadata:
            if "column_description" in context.definition_metadata:
                updated_column_schema = get_metadata_schema(
                    obj.collect_schema(),
                    context.definition_metadata["column_description"],
                )
            else:
                updated_column_schema = get_metadata_schema(obj.collect_schema())

            output_metadata["dagster/column_schema"] = updated_column_schema

        output_metadata.update(
            {
                "preview": MetadataValue.md(markdown_preview),
                "dagster/row_count": get_lazyframe_num_rows(obj),
            }
        )

        obj.sink_parquet(f"{target_uri.rstrip('/')}/part-00000.parquet", mkdir=True)

        context.add_output_metadata(output_metadata)

    @override
    def load_input(self, context: InputContext) -> LazyFrame:
        assert context.upstream_output is not None, "echo no upstream output found"
        assert context.upstream_output.definition_metadata is not None, (
            f"upstream asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.upstream_output.definition_metadata, (
            f"upstream asset must set metadata {DAGSTER_URI}"
        )

        target_uri = context.upstream_output.definition_metadata[DAGSTER_URI]
        return scan_parquet(_parquet_dataset_glob(target_uri))


@definitions
def defs() -> Definitions:
    return Definitions(
        resources={
            "aemo_deltalake_append_io_manager": PolarsDataFrameSinkDeltaIoManager(
                sink_delta_kwargs={
                    "mode": "append",
                    "delta_write_options": {
                        "schema_mode": "merge",
                    },
                }
            ),
            "aemo_deltalake_overwrite_io_manager": PolarsDataFrameSinkDeltaIoManager(
                sink_delta_kwargs={
                    "mode": "overwrite",
                    "delta_write_options": {
                        "schema_mode": "merge",
                    },
                }
            ),
            "aemo_deltalake_ingest_partitioned_append_io_manager": PolarsDataFrameSinkDeltaIoManager(
                sink_delta_kwargs={
                    "mode": "append",
                    "delta_write_options": {
                        "partition_by": "ingested_date",
                        "schema_mode": "merge",
                    },
                },
            ),
            "aemo_parquet_overwrite_io_manager": PolarsDataFrameSinkParquetIoManager(),
        }
    )

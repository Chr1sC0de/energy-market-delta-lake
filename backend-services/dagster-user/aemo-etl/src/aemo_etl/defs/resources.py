"""Shared Dagster resources and IO managers for aemo-etl."""

from typing import Final, override

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
from dagster_aws.s3 import S3Resource, s3_pickle_io_manager
from polars import LazyFrame, scan_delta, scan_parquet

from aemo_etl.configs import DAGSTER_URI, IO_MANAGER_BUCKET
from aemo_etl.utils import get_lazyframe_num_rows, get_metadata_schema, table_exists

CURRENT_STATE_DELTA_MERGE_OPTIONS: Final = {
    "predicate": "source.surrogate_key = target.surrogate_key",
    "source_alias": "source",
    "target_alias": "target",
}
CURRENT_STATE_MERGE_UPDATE_PREDICATE: Final = (
    "target.source_content_hash IS NULL OR "
    "source.source_content_hash != target.source_content_hash"
)


class PolarsDataFrameSinkDeltaIoManager(ConfigurableIOManager):
    """IO manager that writes Polars lazy frames to Delta tables."""

    sink_delta_kwargs: dict[str, Any] = {}
    scan_delta_kwargs: dict[str, Any] = {}
    merge_update_predicate: str | None = None

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        """Write output frames to Delta and handle merge mode as an upsert."""
        assert context.definition_metadata is not None, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.definition_metadata, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        target_uri = context.definition_metadata[DAGSTER_URI]

        row_count = get_lazyframe_num_rows(obj)

        mode = self.sink_delta_kwargs.get("mode", "error")
        target_exists = True
        if row_count == 0 or mode == "merge":
            target_exists = table_exists(target_uri)

        if row_count > 0 or not target_exists:
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
                    "sink_delta_kwargs": MetadataValue.json(self.sink_delta_kwargs),
                    "dagster/row_count": row_count,
                }
            )

            sink_delta_kwargs = self.sink_delta_kwargs
            if mode == "merge" and not target_exists:
                sink_delta_kwargs = {
                    key: value
                    for key, value in self.sink_delta_kwargs.items()
                    if key != "delta_merge_options"
                }
                sink_delta_kwargs["mode"] = "append"

            return_object = obj.sink_delta(target_uri, **sink_delta_kwargs)

            if mode == "merge" and target_exists:
                assert return_object is not None, (
                    "mode was set to merge but resulting output is None"
                )

                context.log.info(f"merging data with settings {self.sink_delta_kwargs}")

                merge_results = (
                    return_object.when_matched_update_all(
                        predicate=self.merge_update_predicate
                    )
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
    """IO manager that writes Polars lazy frames as parquet datasets."""

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        assert context.definition_metadata is not None, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        assert DAGSTER_URI in context.definition_metadata, (
            f"asset must set metadata {DAGSTER_URI}"
        )
        target_uri = context.definition_metadata[DAGSTER_URI]

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
    """Provide the shared Dagster resources for loaded definitions."""
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
            "aemo_deltalake_current_state_merge_io_manager": PolarsDataFrameSinkDeltaIoManager(
                sink_delta_kwargs={
                    "mode": "merge",
                    "delta_merge_options": CURRENT_STATE_DELTA_MERGE_OPTIONS,
                },
                merge_update_predicate=CURRENT_STATE_MERGE_UPDATE_PREDICATE,
            ),
            "aemo_parquet_overwrite_io_manager": PolarsDataFrameSinkParquetIoManager(),
            "s3": S3Resource(),
            "io_manager": s3_pickle_io_manager.configured(
                {
                    "s3_bucket": IO_MANAGER_BUCKET,
                    "s3_prefix": "dagster/storage",
                }
            ),
        }
    )

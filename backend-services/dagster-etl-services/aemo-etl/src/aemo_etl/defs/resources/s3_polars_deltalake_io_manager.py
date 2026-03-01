from typing import cast, override

from dagster import (
    Any,
    ConfigurableIOManager,
    InputContext,
    MetadataValue,
    OutputContext,
)
from polars import DataFrame, LazyFrame, scan_delta

from aemo_etl.utils import get_metadata_schema


class PolarsDataFrameSinkDeltaIoManager(ConfigurableIOManager):
    root: str
    skip_prefix: int = 1
    sink_delta_kwargs: dict[str, Any] = {}
    scan_delta_kwargs: dict[str, Any] = {}
    preview_row_count: int = 5

    @override
    def handle_output(self, context: OutputContext, obj: LazyFrame) -> None:
        """automatically handles merges as upserts"""
        key_prefix = "/".join(context.asset_key.parts[self.skip_prefix :])
        target_uri = f"{self.root}/{key_prefix}"

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

        markdown_preview = (
            cast(DataFrame, obj.head(self.preview_row_count).collect())
            .to_pandas()
            .to_markdown()
        )

        if "dagster/column_schema" not in context.definition_metadata:
            if "column_description" in context.definition_metadata:
                column_schema = get_metadata_schema(
                    obj.collect_schema(),
                    context.definition_metadata["column_description"],
                )
            else:
                column_schema = get_metadata_schema(obj.collect_schema())

        output_metadata = {
            "dagster/uri": target_uri,
            "dagster/table_name": context.asset_key.parts[-1],
            "dagster/column_schema": column_schema,
            "preview": MetadataValue.md(markdown_preview),
            "sink_delta_kwargs": MetadataValue.json(self.sink_delta_kwargs),
        }

        context.add_output_metadata(output_metadata)

    @override
    def load_input(self, context: InputContext) -> LazyFrame:
        key_prefix = "/".join(context.asset_key.parts[self.skip_prefix :])
        target_uri = f"{self.root}/{key_prefix}"
        return scan_delta(target_uri, **self.scan_delta_kwargs)

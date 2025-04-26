from typing import Any, Callable, override

import dagster as dg
import polars as pl
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError
from pydantic import BaseModel, ConfigDict

from aemo_gas import factory, utils
from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET
from aemo_gas.vichub import assets


class PreviewBuilder(factory.ops.GetDataFrameFromSourceFilesMetaDataBuilderBase):
    @override
    def __call__(
        self,
        context: dg.OpExecutionContext,
        current_df: pl.LazyFrame,
        source_bucket: str,
        target_bucket: str,
        target_s3_prefix: str,
        target_name: str,
        df_schema: dict[str, pl.DataType],
        op_metadata: dict[str, Any],
    ) -> dict[str, dg.MetadataValue]:
        metadata: dict[str, dg.MetadataValue] = {}
        # get a preview of the dataframe from the existing delta table
        preview_delta_table_path = (
            f"s3://{target_bucket}/{target_s3_prefix}/{target_name}"
        )
        context.log.info(f"adding preview: {preview_delta_table_path}")
        df_preview = utils.get_table(preview_delta_table_path)

        if df_preview is None:
            df_preview = current_df
            context.log.info(
                f"{preview_delta_table_path} not found, previewing using upserted rows"
            )

        metadata["preview"] = dg.MetadataValue.md(
            df_preview.head()
            .collect()
            .to_pandas()
            .to_markdown()  # use the pandas markdown, it's better than the polars markdown
        )
        return metadata


class MibbDeltaTableAssetFactoryConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)  # pyright: ignore[reportUnannotatedClassAttribute]

    io_manager_key: str
    group_name: str
    key_prefix: list[str]

    source_bucket: str = LANDING_BUCKET
    source_s3_prefix: str
    source_s3_glob: str

    target_bucket: str = BRONZE_BUCKET
    target_s3_prefix: str
    target_s3_name: str

    df_schema: dict[str, type[pl.DataType]]

    description: str | None = None
    metadata: dict[str, Any] | None = None

    post_process_hook: Callable[[pl.LazyFrame], pl.LazyFrame] | None = None

    metadata_builders: (
        list[factory.ops.GetDataFrameFromSourceFilesMetaDataBuilderBase] | None
    ) = [PreviewBuilder()]


def delta_table(
    config: MibbDeltaTableAssetFactoryConfig,
) -> dg.AssetsDefinition:
    @dg.graph_asset(
        group_name=config.group_name,
        key_prefix=config.key_prefix,
        name=config.target_s3_name,
        description=config.description,
        kinds={"deltalake", "table"},
    )
    def asset() -> pl.LazyFrame:
        s3_object_keys = factory.ops.get_s3_object_keys_from_prefix_factory(
            bucket=config.source_bucket,
            search_prefix=config.source_s3_prefix,
            file_glob=config.source_s3_glob,
        )()
        df = factory.ops.get_dataframe_from_source_files(
            source_bucket=config.source_bucket,
            target_bucket=config.target_bucket,
            target_s3_prefix=config.target_s3_prefix,
            target_name=config.target_s3_name,
            io_manager_key=config.io_manager_key,
            df_schema=config.df_schema,
            metadata=config.metadata,
            post_process_hook=config.post_process_hook,
            metadata_builders=config.metadata_builders,
        )(s3_object_keys)
        return df

    return asset


def compact_and_vacuum(
    table_definition: dg.AssetsDefinition,
    group_name: str,
    key_prefix: list[str],
    table_name: str,
    retention_hours: int = 0,
    automation_condition: dg.AutomationCondition[Any] | None = None,
):
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name="compact_and_vacuum",
        description=f"compact and vacuum for {table_name}",
        deps=[table_definition],
        kinds={"task"},
        automation_condition=automation_condition,
    )
    def _compact_and_vacuum(context: dg.AssetExecutionContext):
        delta_table_path = f"s3://{BRONZE_BUCKET}/aemo/gas/{'/'.join(key_prefix[-2:])}"

        context.log.info(f"running compact and vacuum for {delta_table_path}")

        try:
            delta_table = DeltaTable(delta_table_path)
        except TableNotFoundError:
            context.log.info(f"table not found {delta_table_path}")
            raise

        metadata = {}

        compacted_response = delta_table.optimize.compact()

        for key, value in compacted_response.items():
            metadata[key] = value

        metadata["vacuumed"] = delta_table.vacuum(
            retention_hours=retention_hours,
            enforce_retention_duration=False,
            dry_run=False,
        )

        context.add_asset_metadata(metadata)

    return _compact_and_vacuum

import pathlib as pt
from typing import Any

from dagster import AssetExecutionContext, AssetsDefinition, AutomationCondition, asset
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError

# pyright: reportUnknownMemberType=false, reportAny=false, reportUnknownArgumentType=false, reportExplicitAny=false


def compact_and_vacuum_dataframe_asset_factory(
    group_name: str,
    key_prefix: list[str],
    s3_target_bucket: str,
    s3_target_prefix: str,
    s3_target_table_name: str,
    retention_hours: int | None = 0,
    dependant_definitions: list[AssetsDefinition] | None = None,
    storage_options: dict[str, str] | None = None,
    automation_condition: AutomationCondition | None = None,
    # useful for testing purposes
    table_path_override: pt.Path | None = None,
    captured_response: dict[str, Any] | None = None,
):
    @asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name=f"{s3_target_table_name}_compact_and_vacuum",
        description=f"compact and vacuum for {s3_target_table_name}",
        deps=dependant_definitions,
        kinds={"task"},
        automation_condition=automation_condition,
    )
    def compact_and_vacuum(context: AssetExecutionContext):
        delta_table_path = (
            f"s3://{s3_target_bucket}/{s3_target_prefix}/{s3_target_table_name}"
        )

        if table_path_override is not None:
            delta_table_path = table_path_override

        context.log.info(f"running compact and vacuum for {delta_table_path}")

        try:
            delta_table = DeltaTable(delta_table_path, storage_options=storage_options)
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

        try:
            context.add_asset_metadata(metadata)
        except AttributeError:
            context.log.info("unable to add asset metadata")
            if captured_response is not None:
                for key, value in metadata.items():
                    captured_response[key] = value

    return compact_and_vacuum

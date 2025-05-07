import pathlib as pt
from typing import Any

import dagster as dg
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError

# pyright: reportUnknownMemberType=false, reportAny=false, reportUnknownArgumentType=false, reportExplicitAny=false


def compact_and_vacuum_dataframe_asset_factory(
    group_name: str,
    table_bucket: str,
    s3_schema: str,
    table_name: str,
    key_prefix: list[str],
    retention_hours: int = 0,
    dependant_definitions: list[dg.AssetsDefinition] | None = None,
    storage_options: dict[str, str] | None = None,
    # used for purposes
    table_path_override: pt.Path | None = None,
    # use for testing purposes
    captured_response: dict[str, Any] | None = None,
):
    @dg.asset(
        group_name=group_name,
        key_prefix=key_prefix,
        name=f"{table_name}_compact_and_vacuum",
        description=f"compact and vacuum for {table_name}",
        deps=dependant_definitions,
        kinds={"task"},
    )
    def compact_and_vacuum(context: dg.AssetExecutionContext):
        delta_table_path = f"s3://{table_bucket}/{s3_schema}/{table_name}"

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

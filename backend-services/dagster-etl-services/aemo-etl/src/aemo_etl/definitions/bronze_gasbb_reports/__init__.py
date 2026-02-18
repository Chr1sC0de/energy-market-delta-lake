"""GASBB report definitions - generated from registry."""

from aemo_etl.configuration.gasbb import GASBB_CONFIGS
from aemo_etl.configuration.gasbb.hooks import get_hooks_for_report
from aemo_etl.definitions.bronze_gasbb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list

# Loop through all registered GASBB configs and create definitions
for config in GASBB_CONFIGS.values():
    # Get hooks for this report (if any)
    hooks = get_hooks_for_report(config.table_name)

    # Create definition builder with config and hooks
    definition_builder = definition_builder_factory(
        config=config,
        process_object_hook=hooks.get("process_object_hook"),
        preprocess_hook=hooks.get("preprocess_hook"),
        post_process_hook=hooks.get("post_process_hook"),
        datetime_pattern=hooks.get("datetime_pattern"),
        datetime_column_name=hooks.get("datetime_column_name"),
    )

    # Build and register definition
    definitions_list.append(definition_builder.build())

__all__ = ["GASBB_CONFIGS"]

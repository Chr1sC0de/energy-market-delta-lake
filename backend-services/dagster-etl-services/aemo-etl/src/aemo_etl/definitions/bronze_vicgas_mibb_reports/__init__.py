"""MIBB report definitions - generated from registry."""

from aemo_etl.configuration.mibb import MIBB_CONFIGS
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list

# Loop through all registered MIBB configs and create definitions
for config in MIBB_CONFIGS.values():
    # Create definition builder with config
    definition_builder = definition_builder_factory(config)

    # Build and register definition
    definitions_list.append(definition_builder.build())

__all__ = ["MIBB_CONFIGS"]

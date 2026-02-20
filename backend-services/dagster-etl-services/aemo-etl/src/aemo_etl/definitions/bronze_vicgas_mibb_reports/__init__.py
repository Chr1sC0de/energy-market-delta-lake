"""MIBB report definitions - generated from registry."""

from aemo_etl.factory.definition import GetMibbReportFromS3FilesDefinitionBuilder

from aemo_etl.configuration.registry import MIBB_CONFIGS
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.register import definitions_list

definition_builders: list[GetMibbReportFromS3FilesDefinitionBuilder] = []

# Loop through all registered MIBB configs and create definitions
for config in MIBB_CONFIGS.values():
    # Create definition builder with config
    definition_builder = definition_builder_factory(config)

    definition_builders.append(definition_builder)

    # Build and register definition
    definitions_list.append(definition_builder.build())

__all__ = ["MIBB_CONFIGS"]

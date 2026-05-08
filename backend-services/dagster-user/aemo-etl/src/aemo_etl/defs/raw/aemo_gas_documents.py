"""AEMO gas PDF source-page discovery definitions."""

from dagster import Definitions, definitions

from aemo_etl.factories.aemo_gas_documents.definitions import (
    aemo_gas_document_sources_definitions_factory,
)


@definitions
def defs() -> Definitions:
    """Register the AEMO gas document source metadata asset."""
    return aemo_gas_document_sources_definitions_factory()

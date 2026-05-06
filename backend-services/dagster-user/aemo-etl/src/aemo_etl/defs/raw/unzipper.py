from dagster import Definitions, definitions

from aemo_etl.factories.unzipper.definitions import unzipper_definitions_factory


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        unzipper_definitions_factory(
            domain="vicgas",
            name="unzipper_vicgas",
        ),
        unzipper_definitions_factory(
            domain="gbb",
            name="unzipper_gbb",
        ),
        unzipper_definitions_factory(
            domain="sttm",
            name="unzipper_sttm",
        ),
    )

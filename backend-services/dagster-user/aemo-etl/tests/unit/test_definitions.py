"""Unit tests for the root aemo_etl/definitions.py module."""

from dagster import Definitions
from pytest_mock import MockerFixture


def test_root_defs_function(mocker: MockerFixture) -> None:
    """defs() merges resources, loaded definitions, and maintenance definitions."""
    mocker.patch(
        "aemo_etl.definitions.load_from_defs_folder",
        return_value=Definitions(),
    )
    from aemo_etl.definitions import defs
    from aemo_etl.maintenance.delta_tables import DELTA_TABLE_VACUUM_JOB_NAME

    result = defs()
    assert isinstance(result, Definitions)
    assert [job.name for job in result.jobs or []] == [DELTA_TABLE_VACUUM_JOB_NAME]

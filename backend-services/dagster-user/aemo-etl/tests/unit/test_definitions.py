"""Unit tests for the root aemo_etl/definitions.py module."""

from dagster import Definitions
from pytest_mock import MockerFixture


def test_root_defs_function(mocker: MockerFixture) -> None:
    """defs() merges resources with load_from_defs_folder output."""
    mocker.patch(
        "aemo_etl.definitions.load_from_defs_folder",
        return_value=Definitions(),
    )
    from aemo_etl.definitions import defs

    result = defs()
    assert isinstance(result, Definitions)
